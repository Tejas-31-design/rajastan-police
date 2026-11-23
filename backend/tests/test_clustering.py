"""
Tests for the clustering engine — 4 test cases.
"""

import pytest
from datetime import datetime

from app.models import Campaign, Indicator, Report
from app.ml.clustering import rebuild_campaigns, build_campaign_graph, _extract_indicator_key


def _make_report(db, content, source_type, risk_score, label, district, indicators):
    r = Report(
        created_at=datetime.utcnow(),
        source_type=source_type,
        content=content,
        risk_score=risk_score,
        label=label,
        reasons=["Test reason"],
        indicators=indicators,
        next_steps=[],
        signals=[],
        district=district,
    )
    db.add(r)
    db.flush()
    return r


class TestClustering:
    def test_shared_domain_clusters(self, db_session):
        """Reports sharing a domain should be in the same campaign."""
        r1 = _make_report(db_session, "SMS A", "sms", 80, "High Risk", "Jaipur",
                          {"domain": "sbi-kyc.xyz", "phones": [], "upis": []})
        r2 = _make_report(db_session, "SMS B", "sms", 75, "High Risk", "Jaipur",
                          {"domain": "sbi-kyc.xyz", "phones": [], "upis": []})
        r3 = _make_report(db_session, "Safe URL", "url", 10, "Safe", "Jodhpur",
                          {"domain": "google.com", "phones": [], "upis": []})
        db_session.commit()

        rebuild_campaigns(db_session)

        camp_ids = {r.campaign_id for r in [r1, r2]}
        db_session.refresh(r1)
        db_session.refresh(r2)
        db_session.refresh(r3)

        assert r1.campaign_id is not None
        assert r2.campaign_id is not None
        assert r1.campaign_id == r2.campaign_id, "Shared domain reports should be in same campaign"

    def test_shared_phone_clusters(self, db_session):
        """Reports sharing a phone number should cluster together."""
        r1 = _make_report(db_session, "Job scam A", "sms", 70, "High Risk", "Kota",
                          {"phones": ["9999888877"], "upis": []})
        r2 = _make_report(db_session, "Job scam B", "sms", 65, "High Risk", "Kota",
                          {"phones": ["9999888877"], "upis": []})
        db_session.commit()

        rebuild_campaigns(db_session)
        db_session.refresh(r1)
        db_session.refresh(r2)

        assert r1.campaign_id == r2.campaign_id

    def test_indicator_extraction(self):
        """_extract_indicator_key should return all indicator types."""
        r = Report(
            id=99,
            content="test",
            source_type="sms",
            risk_score=80,
            label="High Risk",
            reasons=[],
            indicators={
                "domain": "scam.xyz",
                "phones": ["9876543210"],
                "upis": ["fake@upi"],
            },
            signals=[],
            next_steps=[],
            district="Jaipur",
        )
        keys = _extract_indicator_key(r)
        types = [k[0] for k in keys]
        assert "domain" in types
        assert "phone" in types
        assert "upi" in types

    def test_campaign_graph_structure(self, db_session):
        """build_campaign_graph should return nodes and links."""
        campaign = Campaign(
            name="Test Campaign",
            report_count=2,
            risk_level="High",
            indicators={"domains": ["test.xyz"]},
            status="active",
            district="Jaipur",
            description="test",
        )
        db_session.add(campaign)
        db_session.flush()

        r = _make_report(db_session, "Test report", "url", 80, "High Risk", "Jaipur",
                         {"domain": "test.xyz"})
        r.campaign_id = campaign.id

        ind = Indicator(
            type="domain",
            value="test.xyz",
            report_count=1,
            campaign_id=campaign.id,
            first_seen=datetime.utcnow(),
            last_seen=datetime.utcnow(),
        )
        db_session.add(ind)
        db_session.commit()

        graph = build_campaign_graph(campaign, [r], [ind])
        assert "nodes" in graph
        assert "links" in graph
        assert len(graph["nodes"]) >= 2  # report node + indicator node
        assert len(graph["links"]) >= 1
