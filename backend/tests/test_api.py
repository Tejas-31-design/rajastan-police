"""
API integration tests — tests FastAPI endpoints with TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# In-memory SQLite for tests
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=TEST_ENGINE)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestHealthEndpoint:
    def test_health_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


class TestCheckURLEndpoint:
    def test_phishing_url_high_risk(self, client):
        resp = client.post("/api/check/url", json={"url": "sbi-kyc-update.xyz"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_score"] >= 70
        assert data["label"] == "High Risk"
        assert len(data["reasons"]) >= 3

    def test_safe_url(self, client):
        resp = client.post("/api/check/url", json={"url": "https://www.google.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] == "Safe"
        assert data["risk_score"] <= 30

    def test_invalid_empty_url(self, client):
        resp = client.post("/api/check/url", json={"url": ""})
        assert resp.status_code == 422  # Validation error

    def test_response_has_signals(self, client):
        resp = client.post("/api/check/url", json={"url": "http://sbi-kyc.xyz"})
        data = resp.json()
        assert "signals" in data
        assert len(data["signals"]) > 0


class TestCheckSMSEndpoint:
    def test_hinglish_scam_sms(self, client):
        resp = client.post("/api/check/sms", json={
            "text": "Aapka SBI account block ho jayega, KYC update karein: http://sbi-kyc-update.xyz"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] != "Safe"
        assert data["risk_score"] >= 50

    def test_safe_otp_sms(self, client):
        resp = client.post("/api/check/sms", json={
            "text": "Your OTP for SBI Net Banking is 123456. Valid for 10 minutes. Do NOT share."
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["label"] == "Safe"

    def test_sms_response_shape(self, client):
        resp = client.post("/api/check/sms", json={"text": "Hello, test message."})
        data = resp.json()
        assert all(k in data for k in ["risk_score", "label", "reasons", "indicators", "next_steps", "signals"])


class TestDashboardEndpoint:
    def test_stats_endpoint(self, client):
        resp = client.get("/api/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "reports_today" in data
        assert "active_campaigns" in data
        assert "high_risk_domains" in data
        assert "top_district" in data

    def test_trend_endpoint(self, client):
        resp = client.get("/api/dashboard/trend")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 14  # 14 days

    def test_hotspots_endpoint(self, client):
        resp = client.get("/api/dashboard/hotspots")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)


class TestCampaignsEndpoint:
    def test_list_campaigns(self, client):
        resp = client.get("/api/campaigns")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_campaign_404(self, client):
        resp = client.get("/api/campaigns/99999")
        assert resp.status_code == 404
