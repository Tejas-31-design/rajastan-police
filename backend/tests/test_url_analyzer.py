"""
Tests for the URL analyzer — 7 test cases.
"""

import pytest
from app.ml.url_analyzer import URLAnalyzer


@pytest.fixture(scope="module")
def analyzer():
    return URLAnalyzer.get_instance()


class TestURLAnalyzerHighRisk:
    def test_sbi_kyc_phishing_url(self, analyzer):
        """Acceptance check: sbi-kyc-update.xyz must be High Risk with 3+ reasons."""
        result = analyzer.analyze("sbi-kyc-update.xyz")
        assert result["risk_score"] >= 70, f"Expected ≥70, got {result['risk_score']}"
        assert result["label"] == "High Risk"
        assert len(result["reasons"]) >= 3, f"Expected ≥3 reasons, got {result['reasons']}"

    def test_phishing_no_https(self, analyzer):
        result = analyzer.analyze("http://hdfc-verify-account.top/secure")
        assert result["risk_score"] >= 65
        assert result["label"] in ("High Risk", "Suspicious")
        # Should flag no-HTTPS
        triggered = [s for s in result["signals"] if s["name"] == "No HTTPS" and s["triggered"]]
        assert triggered, "Expected 'No HTTPS' signal to be triggered"

    def test_suspicious_tld_xyz(self, analyzer):
        result = analyzer.analyze("http://paytm-reward-claim.xyz")
        assert result["risk_score"] >= 60
        tld_signal = [s for s in result["signals"] if "TLD" in s["name"]]
        assert any(s["triggered"] for s in tld_signal)

    def test_homoglyph_domain(self, analyzer):
        result = analyzer.analyze("http://sbi0nline.xyz/kyc")
        assert result["risk_score"] >= 60
        assert any("Homoglyph" in r or "0" in r or "digit" in r.lower() for r in result["reasons"])


class TestURLAnalyzerSafe:
    def test_google_safe(self, analyzer):
        """Acceptance check: google.com must be Safe."""
        result = analyzer.analyze("google.com")
        assert result["risk_score"] <= 30, f"Expected ≤30 for google.com, got {result['risk_score']}"
        assert result["label"] == "Safe"

    def test_sbi_official_safe(self, analyzer):
        result = analyzer.analyze("https://www.sbi.co.in")
        assert result["label"] == "Safe"
        assert result["risk_score"] <= 25

    def test_https_flag(self, analyzer):
        result_https = analyzer.analyze("https://www.hdfcbank.com")
        result_http = analyzer.analyze("http://sbi-kyc-update.xyz")
        https_signal = [s for s in result_https["signals"] if s["name"] == "No HTTPS"][0]
        http_signal = [s for s in result_http["signals"] if s["name"] == "No HTTPS"][0]
        assert not https_signal["triggered"]
        assert http_signal["triggered"]


class TestURLAnalyzerResponse:
    def test_response_shape(self, analyzer):
        """Every response must include required keys."""
        result = analyzer.analyze("http://sbi-kyc-update.xyz")
        assert "risk_score" in result
        assert "label" in result
        assert "reasons" in result
        assert "indicators" in result
        assert "next_steps" in result
        assert "signals" in result
        assert isinstance(result["signals"], list)
        assert len(result["signals"]) > 0
        assert all("name" in s and "weight" in s and "triggered" in s for s in result["signals"])

    def test_score_range(self, analyzer):
        for url in ["http://sbi-kyc.xyz", "https://google.com", "http://paytm-claim.top"]:
            result = analyzer.analyze(url)
            assert 0 <= result["risk_score"] <= 100
