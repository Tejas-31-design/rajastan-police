"""
Tests for the SMS classifier — 6 test cases.
"""

import pytest
from app.ml.sms_classifier import SMSClassifier, _extract_indicators
from app.ml.url_analyzer import URLAnalyzer


@pytest.fixture(scope="module")
def classifier():
    return SMSClassifier.get_instance()


@pytest.fixture(scope="module")
def url_analyzer():
    return URLAnalyzer.get_instance()


class TestSMSClassifierHighRisk:
    def test_hinglish_sbi_kyc(self, classifier, url_analyzer):
        """Acceptance check: Hinglish KYC SMS must be flagged with link extracted."""
        text = "Aapka SBI account block ho jayega, KYC update karein: http://sbi-kyc-update.xyz"
        result = classifier.analyze(text, url_analyzer=url_analyzer)
        assert result["label"] in ("High Risk", "Suspicious"), f"Expected scam, got {result['label']}"
        assert result["risk_score"] >= 50
        # Link must be extracted
        assert len(result["indicators"]["urls"]) >= 1
        assert "sbi-kyc-update.xyz" in result["indicators"]["urls"][0]

    def test_electricity_scam(self, classifier):
        text = "JVVNL: Aapka electricity connection aaj raat band ho jayega. Turant pay karein: http://jvvnl-bill-pay.xyz"
        result = classifier.analyze(text)
        assert result["risk_score"] >= 50
        assert result["label"] != "Safe"

    def test_prize_scam(self, classifier):
        text = "Congratulations! You have won Rs 50,000 in SBI lucky draw. Claim at http://prize-claim.top"
        result = classifier.analyze(text)
        assert result["risk_score"] >= 55
        assert result["label"] != "Safe"

    def test_job_scam(self, classifier):
        text = "Work from home! Earn Rs 50,000/month. No experience needed. WhatsApp 9876543210"
        result = classifier.analyze(text)
        assert result["risk_score"] >= 40
        # Phone extracted
        assert len(result["indicators"]["phones"]) >= 1


class TestSMSClassifierSafe:
    def test_otp_message_safe(self, classifier):
        text = "Your OTP for SBI Net Banking is 834512. Valid for 10 minutes. Do NOT share with anyone."
        result = classifier.analyze(text)
        assert result["label"] == "Safe"
        assert result["risk_score"] <= 40

    def test_transaction_alert_safe(self, classifier):
        text = "Transaction Alert: Rs 5,000 debited from HDFC A/c XX4521. If not done by you call 18002586161."
        result = classifier.analyze(text)
        assert result["risk_score"] <= 45


class TestIndicatorExtraction:
    def test_phone_extraction(self):
        text = "Call 9876543210 or WhatsApp 9123456789 for more information."
        ind = _extract_indicators(text)
        assert "9876543210" in ind["phones"]
        assert "9123456789" in ind["phones"]

    def test_url_extraction(self):
        text = "Click here: http://sbi-kyc.xyz/update and also www.phishing.top"
        ind = _extract_indicators(text)
        assert any("sbi-kyc.xyz" in u for u in ind["urls"])

    def test_response_shape(self, classifier):
        result = classifier.analyze("Test message with no scam content.")
        assert "risk_score" in result
        assert "label" in result
        assert "reasons" in result
        assert "signals" in result
        assert "indicators" in result
        assert "next_steps" in result
        assert isinstance(result["signals"], list)
