"""
SMS / message classifier — scam-theme detection.

Covers English, Hindi (Devanagari) and Hinglish.
Score = 0.6 × ML (TF-IDF + LogReg) + 0.4 × Rules
"""

from __future__ import annotations

import re
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# ── Patterns ──────────────────────────────────────────────────────────────────

PHONE_RE = re.compile(r'\b(?:\+91[\s-]?)?[6-9]\d{9}\b')
URL_RE = re.compile(
    r'https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z]{2,}/[^\s]*'
)
UPI_RE = re.compile(r'[a-zA-Z0-9._-]+@(?:okaxis|oksbi|okhdfcbank|okicici|ybl|upi|paytm|ibl|axl|sbi|apl|barodampay|kotak|pytm|okbizaxis|timecosmos|waicici)[^@\s]*', re.IGNORECASE)
UPI_GENERIC_RE = re.compile(r'\b[a-zA-Z0-9._-]{3,20}@[a-zA-Z]{3,15}\b')

SCAM_CATEGORIES: dict[str, dict] = {
    "kyc_scam": {
        "keywords": [
            "kyc", "account block", "verify account", "aadhar", "pan card",
            "bank account suspend", "account suspend", "khata band",
            "kyc expire", "kyc update", "acount band", "block ho jayega",
        ],
        "theme": "KYC / Account Block Scam",
        "weight": 25,
    },
    "prize_scam": {
        "keywords": [
            "congratulations", "won", "winner", "prize", "lottery", "reward",
            "lucky draw", "selected", "rs 50000", "badhai", "jeeti",
            "jeet liya", "lucky winner", "claim your",
        ],
        "theme": "Fake Prize / Lottery Scam",
        "weight": 20,
    },
    "loan_scam": {
        "keywords": [
            "instant loan", "personal loan", "no documents", "quick cash",
            "easy money", "loan approved", "pre-approved loan", "bina document",
            "turant loan", "loan mil sakta", "low interest loan",
        ],
        "theme": "Fake Loan Offer",
        "weight": 20,
    },
    "electricity_scam": {
        "keywords": [
            "electricity", "bijli", "power cut", "meter", "electric bill",
            "discom", "jvvnl", "avvnl", "connection cut", "last warning",
            "bijli band", "light band", "power disconnection",
        ],
        "theme": "Electricity Bill Scam",
        "weight": 20,
    },
    "parcel_scam": {
        "keywords": [
            "parcel", "customs", "package held", "delivery hold", "courier",
            "shipment", "customs duty", "release package", "india post",
            "fedex", "dhl", "parcel rok", "customs mein",
        ],
        "theme": "Parcel / Customs Scam",
        "weight": 20,
    },
    "job_scam": {
        "keywords": [
            "work from home", "earn per month", "no experience", "vacancy",
            "recruitment", "ghar baithe paise", "job offer", "data entry",
            "part time job", "online job", "income per day",
        ],
        "theme": "Fake Job Offer",
        "weight": 15,
    },
    "upi_scam": {
        "keywords": [
            "upi refund", "cashback pending", "phonepe cashback",
            "google pay refund", "paytm cashback", "gpay", "bhim upi",
            "scan qr", "upi id send", "refund process",
        ],
        "theme": "UPI Refund / Cashback Scam",
        "weight": 20,
    },
}

HINGLISH_PATTERNS: list[tuple[str, str, int]] = [
    (r'\baccount\s+block\b', "Account block threat (Hinglish)", 15),
    (r'\bkyc\s+(?:update|kare|karein|karo)\b', "KYC update demand (Hinglish)", 15),
    (r'\bverify\s+(?:kare|karein|karo|kijiye)\b', "Verification demand (Hinglish)", 10),
    (r'\b(?:rs\.?\s*[\d,]+|inr\s*[\d,]+)\s*(?:reward|cashback|prize|mila|milega)\b', "Fake reward amount", 15),
    (r'\b(?:link\s+pe|link\s+par)\s+click\b', "Suspicious link instruction (Hinglish)", 10),
    (r'\botp\s+(?:share|mat\s+share|na\s+share)\b', "OTP warning (social engineering)", 10),
    (r'\b(?:aaj|abhi|turant)\s+(?:pay|bheje|click|kare)\b', "Urgency pressure (Hinglish)", 10),
    (r'\bblock\s+ho\s+jayega\b', "Account block threat (Hinglish)", 15),
    (r'\b(?:ghar\s+baithe|work\s+from\s+home)\s+(?:paise|earn|income)\b', "WFH job scam (Hinglish)", 10),
    (r'\b(?:muft|free)\s+(?:recharge|data|cashback)\b', "Free offer (Hinglish)", 10),
    # Devanagari patterns
    (r'खाता\s*बंद', "Account block (Hindi)", 15),
    (r'केवाईसी', "KYC mention (Hindi)", 15),
    (r'इनाम\s*जीता', "Prize won (Hindi)", 15),
    (r'बिजली\s*काट', "Electricity cut (Hindi)", 15),
]

URGENCY_WORDS = [
    "urgent", "immediate", "tonight", "today only", "last warning",
    "expire", "24 hours", "abhi", "turant", "aaj raat", "last chance",
    "do not ignore", "action required",
]


def _extract_indicators(text: str) -> dict[str, list[str]]:
    phones = list({m.group() for m in PHONE_RE.finditer(text)})
    urls = list({m.group() for m in URL_RE.finditer(text)})
    # Prefer domain-specific UPI patterns
    upis = list({m.group() for m in UPI_RE.finditer(text)})
    if not upis:
        # Fallback generic pattern, filtered
        upis = [
            m.group() for m in UPI_GENERIC_RE.finditer(text)
            if not any(m.group().endswith(d) for d in [".com", ".in", ".org", ".net"])
        ]
    return {"phones": phones[:5], "urls": urls[:5], "upis": upis[:5]}


def _build_training_data() -> tuple[list[str], list[str]]:
    samples: list[tuple[str, str]] = [
        # KYC scams
        ("Your SBI account has been blocked. Update KYC immediately at http://sbi-kyc.xyz or your account will be permanently closed.", "kyc_scam"),
        ("Aapka SBI account block ho jayega 24 ghante mein. KYC update karein: http://sbi-kyc-update.xyz", "kyc_scam"),
        ("HDFC Bank: Your account will be suspended. Verify KYC now: http://hdfc-kyc.top", "kyc_scam"),
        ("Dear customer your ICICI Bank account is blocked. Complete KYC verification: http://icici-kyc.click", "kyc_scam"),
        ("Axis Bank: Aapka khata band ho jayega. KYC expire ho gai hai. Abhi link pe click karein: http://axis-kyc.xyz", "kyc_scam"),
        ("URGENT: SBI net banking blocked. Update PAN & Aadhaar KYC at http://sbionline.xyz immediately", "kyc_scam"),
        ("Kotak Mahindra Bank: Your account access blocked due to incomplete KYC. Update: http://kotak-kyc.top", "kyc_scam"),
        # Prize scams
        ("Congratulations! You have won Rs 50,000 in SBI lucky draw. Claim at http://prize-claim.top. Valid 24 hrs.", "prize_scam"),
        ("Aapne IRCTC lucky draw mein Rs 1 lakh ki lottery jeeti! Abhi claim karein: http://irctc-reward.xyz", "prize_scam"),
        ("Lucky winner! You are selected for Rs 25000 reward. Contact 9876543210 immediately to claim prize.", "prize_scam"),
        ("IRCTC Lucky Draw: You won a free first class ticket! Claim now: http://irctc-lucky.top", "prize_scam"),
        ("PhonePe Diwali offer: Aap lucky winner hain! Rs 5000 cashback. Claim: http://phonepe-diwali.xyz", "prize_scam"),
        # Loan scams
        ("Get instant personal loan Rs 5 lakh in 30 minutes. No documents needed. WhatsApp 9876543210", "loan_scam"),
        ("Aadhar card se turant loan milega. Rs 2 lakh bina document ke. Click: http://loan-offer.xyz", "loan_scam"),
        ("Pre-approved personal loan Rs 3 lakh at 0% interest. Apply now: http://instant-loan.click. Limited offer.", "loan_scam"),
        ("Govt approved loan scheme! Rs 10 lakh without guarantor. Apply: http://loan-scheme.xyz", "loan_scam"),
        # Electricity scams
        ("JVVNL: Your electricity connection will be disconnected tonight at 9 PM due to pending bill. Pay immediately: http://jvvnl-pay.xyz", "electricity_scam"),
        ("Bijli vibhag: Aapka meter band ho jayega aaj raat 9 baje. Rs 847 outstanding. Abhi pay kare: 9876543210", "electricity_scam"),
        ("URGENT last warning: electricity disconnection tonight. Pay outstanding dues: http://discom-pay.top", "electricity_scam"),
        ("AVVNL notice: Unpaid bill Rs 1240. Connection will be cut in 2 hours. Pay now: http://avvnl-bill.xyz", "electricity_scam"),
        # Parcel scams
        ("Your Amazon parcel is held at customs. Pay duty Rs 299 to release: http://customs-pay.xyz. Package ID: IN8827443", "parcel_scam"),
        ("DHL Express: Your international package is at customs. Pay import duty Rs 199: http://dhl-customs.top", "parcel_scam"),
        ("India Post: Aapka parcel customs mein rok diya gaya hai. Rs 149 pay karein release ke liye: http://post-parcel.xyz", "parcel_scam"),
        ("FedEx: Shipment on hold due to customs clearance. Pay Rs 350 to deliver: http://fedex-customs.xyz", "parcel_scam"),
        # Job scams
        ("Work from home opportunity! Earn Rs 50,000/month. No experience needed. Part time. WhatsApp 9123456789", "job_scam"),
        ("Ghar baithe paise kamao. Rs 500 per hour data entry work. Genuine. No investment. Contact: 9876543210", "job_scam"),
        ("Online job available. Rs 15000-25000 monthly. Work 2-3 hours daily. Apply: http://job-offer.xyz", "job_scam"),
        # UPI scams
        ("PhonePe cashback Rs 5000 pending from last month. Claim via UPI: payment@scam. Click: http://phonepe-claim.top", "upi_scam"),
        ("Google Pay refund of Rs 2000 is pending in your account. Add UPI: refund@upi to receive amount.", "upi_scam"),
        ("Paytm cashback Rs 1500 available. Scan QR or send request to: cashback@paytm. Limited time offer!", "upi_scam"),
        # Safe messages
        ("Your OTP for SBI Net Banking login is 834512. Valid for 10 minutes. Do NOT share with anyone.", "safe"),
        ("Transaction Alert: Rs 5,000 debited from HDFC A/c XX4521. Bal Rs 12,340. If not done by you call 18002586161.", "safe"),
        ("Your Flipkart order #OD123456789 has been shipped. Expected delivery: 25 Nov. Track: fk.me/track", "safe"),
        ("Reminder: Your appointment with Dr. Sharma is tomorrow at 10 AM at Jaipur Hospital, Malviya Nagar.", "safe"),
        ("Rajasthan Police: Emergency helpline number 112. Report cybercrime at cybercrime.gov.in or 1930.", "safe"),
        ("IRCTC: PNR 1234567890 confirmed. Train 12955 Mumbai Superfast. Coach S3 Seat 45. Depart 18:30.", "safe"),
        ("Jio: Your monthly recharge of Rs 299 is successful. Validity 28 days. Data balance: 1.5 GB/day.", "safe"),
        ("Aapka electricity bill Rs 1,250 successfully paid. Transaction ID: TXN20241123001. JVVNL receipt generated.", "safe"),
        ("Amazon: Your order has been delivered. Rate your experience at amazon.in. Order ID: 408-1234567-9876543", "safe"),
        ("HDFC Bank: Your credit card bill of Rs 8,450 is due on 5 Dec. Pay at hdfcbank.com or call 18002586161.", "safe"),
    ]
    texts = [s[0] for s in samples]
    labels = [s[1] for s in samples]
    return texts, labels


class SMSClassifier:
    """Explainable SMS scam classifier (TF-IDF + LogReg + rules)."""

    _instance: "SMSClassifier | None" = None

    def __init__(self) -> None:
        self._pipeline: Pipeline | None = None
        self._classes: list[str] = []
        self._train()

    @classmethod
    def get_instance(cls) -> "SMSClassifier":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _train(self) -> None:
        texts, labels = _build_training_data()
        self._pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 3),
                min_df=1,
                max_features=2000,
                analyzer="word",
                sublinear_tf=True,
            )),
            ("clf", LogisticRegression(
                random_state=42,
                max_iter=1000,
                C=2.0,
                class_weight="balanced",
            )),
        ])
        self._pipeline.fit(texts, labels)
        self._classes = list(self._pipeline.classes_)

    def analyze(self, text: str, url_analyzer: Any = None) -> dict[str, Any]:
        if url_analyzer is None:
            try:
                from app.ml.url_analyzer import URLAnalyzer
                url_analyzer = URLAnalyzer.get_instance()
            except Exception:
                url_analyzer = None

        assert self._pipeline is not None

        pred_label: str = self._pipeline.predict([text])[0]
        proba: np.ndarray = self._pipeline.predict_proba([text])[0]
        pred_proba_max: float = float(proba.max())

        is_scam = pred_label != "safe"
        ml_score = pred_proba_max * 100 if is_scam else (1.0 - pred_proba_max) * 100

        # ── Rules engine ──────────────────────────────────────────────────────
        signals: list[dict[str, Any]] = []
        reasons: list[str] = []
        rules_hits: float = 0.0

        text_lower = text.lower()

        # Hinglish / Devanagari patterns
        for pattern, reason, weight in HINGLISH_PATTERNS:
            triggered = bool(re.search(pattern, text, re.IGNORECASE))
            signals.append({"name": reason, "weight": weight, "triggered": triggered})
            if triggered:
                rules_hits += weight
                reasons.append(reason)

        # Category keyword signals
        has_category_match = False
        for cat_key, cat_info in SCAM_CATEGORIES.items():
            matched = any(kw in text_lower for kw in cat_info["keywords"])
            signals.append({
                "name": cat_info["theme"],
                "weight": cat_info["weight"],
                "triggered": matched,
            })
            if matched:
                rules_hits += cat_info["weight"]
                reasons.append(f"Matches {cat_info['theme']} pattern")
                has_category_match = True

        # Urgency language
        has_urgency = any(w in text_lower for w in URGENCY_WORDS)
        signals.append({"name": "Urgency / Threat Language", "weight": 10, "triggered": has_urgency})
        if has_urgency:
            rules_hits += 10
            reasons.append("Uses urgent or threatening language to pressure the recipient")

        # Extract indicators
        indicators = _extract_indicators(text)

        # Embedded URL analysis
        embedded_max_score = 0.0
        if indicators["urls"] and url_analyzer is not None:
            for url in indicators["urls"][:3]:
                try:
                    url_result = url_analyzer.analyze(url)
                    score = url_result["risk_score"]
                    embedded_max_score = max(embedded_max_score, score)
                    if score >= 55:
                        reasons.append(f"Embedded suspicious URL detected: {url[:60]}")
                        signals.append({
                            "name": "Suspicious Embedded URL",
                            "weight": 25,
                            "triggered": True,
                        })
                        rules_hits += 25
                except Exception:
                    pass

        if indicators["phones"]:
            signals.append({"name": "Phone Number Extracted", "weight": 8, "triggered": True})
            reasons.append(f"Contains phone number: {indicators['phones'][0]}")
            rules_hits += 8
        else:
            signals.append({"name": "Phone Number Extracted", "weight": 8, "triggered": False})

        if indicators["upis"]:
            signals.append({"name": "UPI ID Extracted", "weight": 8, "triggered": True})
            reasons.append(f"Contains UPI ID: {indicators['upis'][0]}")
            rules_hits += 8
        else:
            signals.append({"name": "UPI ID Extracted", "weight": 8, "triggered": False})

        # Normalise rules score
        rules_score = min(rules_hits * 1.5, 100.0)

        # Combined score
        final_score = min((0.6 * ml_score) + (0.4 * rules_score), 100.0)
        # Boost from embedded URLs
        if embedded_max_score > 0:
            final_score = max(final_score, embedded_max_score * 0.75)

        # If explicit scam category keyword matched and there is an embedded URL or phone or urgency
        if has_category_match:
            final_score = max(final_score, 60.0)

        # Legitimate standard OTP detection:
        # e.g., "Your OTP for SBI Net Banking is 834512. Valid for 10 minutes. Do NOT share with anyone."
        is_legit_otp = bool(
            re.search(r'\botp\b', text, re.IGNORECASE)
            and re.search(r'\b\d{4,8}\b', text)
            and not indicators["urls"]
            and not indicators["upis"]
            and any(w in text_lower for w in ["valid for", "do not share", "mat share", "not be shared"])
        )
        if is_legit_otp:
            final_score = 15.0
            reasons = ["Legitimate transactional OTP notification; no external links detected"]

        # Label & next steps
        if final_score >= 70:
            label = "High Risk"
            next_steps = [
                "Do NOT respond, click any link, or share any information",
                "Block this sender immediately",
                "Report at cybercrime.gov.in",
                "Call cyber-crime helpline 1930",
            ]
        elif final_score >= 40:
            label = "Suspicious"
            next_steps = [
                "Do not share personal or financial information",
                "Verify by calling the official helpline number",
                "Report at cybercrime.gov.in if confirmed",
            ]
        else:
            label = "Safe"
            if not reasons:
                reasons = ["No suspicious patterns detected"]
            next_steps = [
                "Message appears legitimate",
                "Always verify before sharing sensitive information",
            ]

        theme = "Unknown"
        if is_scam and pred_label in SCAM_CATEGORIES:
            theme = SCAM_CATEGORIES[pred_label]["theme"]

        return {
            "risk_score": round(final_score, 1),
            "label": label,
            "reasons": list(dict.fromkeys(reasons)) if reasons else ["No suspicious patterns detected"],
            "indicators": {**indicators, "category": theme},
            "next_steps": next_steps,
            "signals": signals[:15],
        }
