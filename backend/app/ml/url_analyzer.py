"""
URL Analyzer — explainable phishing detection.

Score = 0.6 × ML (RandomForest) + 0.4 × Rules
Every verdict returns reasons[], signals[], next_steps[].
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import numpy as np
import tldextract
from rapidfuzz import fuzz
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from app.data.brand_list import (
    DOMAIN_AGE_TABLE,
    INDIAN_BRANDS,
    SAFE_DOMAINS,
    SUSPICIOUS_KEYWORDS,
    SUSPICIOUS_TLDS,
)

# Homoglyph substitution table
HOMOGLYPHS: dict[str, str] = {
    "0": "o", "1": "l", "3": "e", "4": "a",
    "5": "s", "6": "g", "7": "t", "@": "a",
}

FEATURE_NAMES = [
    "url_length",
    "subdomain_depth",
    "digit_ratio",
    "special_char_ratio",
    "has_suspicious_tld",
    "has_suspicious_keywords",
    "is_https",
    "lookalike_score",
    "has_homoglyph",
    "domain_age_score",
    "path_length",
    "num_dots",
]


def _extract_features(url: str) -> dict[str, float]:
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)
    ext = tldextract.extract(url)
    domain: str = ext.domain.lower()
    suffix: str = ext.suffix.lower()
    subdomain: str = ext.subdomain.lower()
    full_domain = f"{domain}.{suffix}"

    # --- Length features ---
    url_length = min(len(url) / 100.0, 3.0)
    path_length = min(len(parsed.path) / 50.0, 3.0)
    num_dots = url.count(".")

    # --- Subdomain depth ---
    subdomain_depth = len(subdomain.split(".")) if subdomain else 0

    # --- Character ratios in domain ---
    digit_ratio = sum(c.isdigit() for c in domain) / max(len(domain), 1)
    special_char_ratio = sum(c in "-_@" for c in domain) / max(len(domain), 1)

    # --- Suspicious TLD ---
    has_suspicious_tld = int(("." + suffix) in SUSPICIOUS_TLDS)

    # --- Suspicious keywords in full URL ---
    url_lower = url.lower()
    has_suspicious_keywords = int(any(kw in url_lower for kw in SUSPICIOUS_KEYWORDS))

    # --- HTTPS ---
    is_https = int(url.startswith("https://"))

    # --- Lookalike / brand impersonation ---
    lookalike_score = 0.0
    if full_domain not in SAFE_DOMAINS:
        for brand in INDIAN_BRANDS:
            score = fuzz.partial_ratio(brand, domain) / 100.0
            if score > lookalike_score:
                lookalike_score = score
        # Only suspicious if brand-like but NOT the actual brand
        if full_domain in SAFE_DOMAINS:
            lookalike_score = 0.0

    # --- Homoglyph attack ---
    normalized = domain
    for digit, letter in HOMOGLYPHS.items():
        normalized = normalized.replace(digit, letter)
    has_homoglyph = int(
        normalized != domain
        and any(brand in normalized for brand in INDIAN_BRANDS)
    )

    # --- Simulated domain age ---
    age_days = DOMAIN_AGE_TABLE.get(full_domain)
    if age_days is None:
        age_days = 30 if has_suspicious_tld else 500
    domain_age_score = max(0.0, 1.0 - age_days / 365.0)  # Higher = newer = riskier

    return {
        "url_length": url_length,
        "subdomain_depth": float(subdomain_depth),
        "digit_ratio": digit_ratio,
        "special_char_ratio": special_char_ratio,
        "has_suspicious_tld": float(has_suspicious_tld),
        "has_suspicious_keywords": float(has_suspicious_keywords),
        "is_https": float(is_https),
        "lookalike_score": lookalike_score,
        "has_homoglyph": float(has_homoglyph),
        "domain_age_score": domain_age_score,
        "path_length": path_length,
        "num_dots": float(min(num_dots, 10)),
    }


def _generate_training_data() -> tuple[np.ndarray, np.ndarray]:
    phishing_urls = [
        "http://sbi-kyc-update.xyz/login",
        "http://sbionline.xyz/kyc-verify",
        "http://hdfc-verify-account.top/secure",
        "http://hdfc-kyc-update.click/update",
        "http://paytm-reward-claim.click/win",
        "http://paytm-cashback-win.xyz/claim",
        "http://rto-challan-pay.xyz/pay",
        "http://rto-echallan-rajasthan.top/fine",
        "http://jvvnl-bill-pay.xyz/urgent",
        "http://discom-urgent-pay.top/cut",
        "http://customs-parcel-release.xyz/pay299",
        "http://irctc-lucky-draw.top/claim",
        "http://phonepe-cashback-offer.xyz/claim",
        "http://indiapost-parcel-hold.xyz/release",
        "http://loan-offer-instant.xyz/apply",
        "http://job-offer-wfh.top/apply",
        "http://upi-refund-claim.click/refund",
        "http://sbi0nline.xyz/login/kyc",
        "http://axisbank-kyc-verify.top/update",
        "http://icici-kyc-block.xyz/verify",
        "http://sbionline-secure.top/kyc/update",
        "http://india-post-parcel.xyz/customs/pay",
        "http://irctc-reward-lucky.top/win/ticket",
        "http://phonepe-free-cashback.xyz/claim",
        "http://hdfc-account-block.click/kyc",
    ]
    safe_urls = [
        "https://www.google.com",
        "https://www.sbi.co.in",
        "https://www.hdfcbank.com",
        "https://www.paytm.com",
        "https://www.irctc.co.in",
        "https://www.amazon.in",
        "https://www.flipkart.com",
        "https://www.phonepe.com",
        "https://www.bsnl.co.in",
        "https://www.airtel.in",
        "https://www.jio.com",
        "https://rajasthan.gov.in",
        "https://cybercrime.gov.in",
        "https://www.incometax.gov.in",
        "https://www.rbi.org.in",
        "https://www.uidai.gov.in",
        "https://www.india.gov.in",
        "https://github.com",
        "https://stackoverflow.com",
        "https://www.icicibank.com",
        "https://www.axisbank.com",
        "https://www.amazon.com",
        "https://www.wikipedia.org",
        "https://www.youtube.com",
        "https://onlinesbi.sbi",
    ]

    X, y = [], []
    for url in phishing_urls:
        feats = _extract_features(url)
        X.append([feats[f] for f in FEATURE_NAMES])
        y.append(1)
    for url in safe_urls:
        feats = _extract_features(url)
        X.append([feats[f] for f in FEATURE_NAMES])
        y.append(0)
    return np.array(X, dtype=float), np.array(y)


class URLAnalyzer:
    """Explainable URL phishing detector (RandomForest + rules)."""

    _instance: "URLAnalyzer | None" = None

    def __init__(self) -> None:
        self._scaler = StandardScaler()
        self._model = RandomForestClassifier(
            n_estimators=200, max_depth=8, random_state=42, class_weight="balanced"
        )
        self._train()

    @classmethod
    def get_instance(cls) -> "URLAnalyzer":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _train(self) -> None:
        X, y = _generate_training_data()
        self._scaler.fit(X)
        self._model.fit(self._scaler.transform(X), y)

    def analyze(self, url: str) -> dict[str, Any]:
        raw = url.strip()
        if not raw.startswith(("http://", "https://")):
            raw_full = "http://" + raw
        else:
            raw_full = raw

        feats = _extract_features(raw_full)
        feature_vec = np.array([[feats[f] for f in FEATURE_NAMES]])
        ml_prob: float = self._model.predict_proba(self._scaler.transform(feature_vec))[0][1]

        ext = tldextract.extract(raw_full)
        full_domain = f"{ext.domain}.{ext.suffix}".lower()

        # ── Rules engine ──────────────────────────────────────────────────────
        signals: list[dict[str, Any]] = []
        reasons: list[str] = []
        rules_hits: float = 0.0

        def add_signal(name: str, weight: float, triggered: bool, reason: str = "") -> None:
            nonlocal rules_hits
            signals.append({"name": name, "weight": weight, "triggered": triggered})
            if triggered:
                rules_hits += weight
                if reason:
                    reasons.append(reason)

        add_signal(
            "No HTTPS", 20, not bool(feats["is_https"]),
            "No HTTPS encryption – data transmitted in plaintext",
        )
        add_signal(
            "Suspicious TLD", 20, bool(feats["has_suspicious_tld"]),
            f"Top-level domain '.{ext.suffix}' commonly used in phishing",
        )
        add_signal(
            "Scam Keywords", 15, bool(feats["has_suspicious_keywords"]),
            "URL contains scam-related keywords (kyc, verify, reward, claim…)",
        )
        add_signal(
            "Brand Lookalike", 20,
            feats["lookalike_score"] > 0.65 and full_domain not in SAFE_DOMAINS,
            f"Domain mimics an Indian brand name (similarity {feats['lookalike_score']:.0%})",
        )
        add_signal(
            "Homoglyph Attack", 15, bool(feats["has_homoglyph"]),
            "Uses digit/character substitution to impersonate a brand (e.g. '0' → 'o')",
        )
        add_signal(
            "Newly Registered Domain", 10, feats["domain_age_score"] > 0.85,
            "Domain registered less than 30 days ago (simulated lookup)",
        )
        add_signal(
            "Deep Subdomain", 5, feats["subdomain_depth"] > 1,
            f"Unusual subdomain depth ({int(feats['subdomain_depth'])} levels)",
        )
        add_signal(
            "High Digit Ratio", 5, feats["digit_ratio"] > 0.3,
            "Excessive digits in domain name – common in algorithmically generated domains",
        )
        add_signal(
            "Long URL", 5, feats["url_length"] > 1.5,
            "Unusually long URL – often used to hide destination",
        )
        add_signal(
            "Special Characters", 5, feats["special_char_ratio"] > 0.1,
            "Special characters in domain can indicate obfuscation",
        )

        # Normalise rules score
        rules_score = min(rules_hits * 1.5, 100.0)

        # Combined score
        final_score = min((0.6 * ml_prob * 100) + (0.4 * rules_score), 100.0)

        # High-confidence phishing boost (e.g. brand lookalike + suspicious TLD + keywords)
        if (bool(feats["has_suspicious_tld"]) and (feats["lookalike_score"] > 0.65 or bool(feats["has_homoglyph"])) and bool(feats["has_suspicious_keywords"])):
            final_score = max(final_score, 85.0)
        elif (bool(feats["has_suspicious_tld"]) and bool(feats["has_suspicious_keywords"])):
            final_score = max(final_score, 75.0)

        # Legitimate domain check
        if full_domain in SAFE_DOMAINS:
            final_score = min(final_score, 15.0)

        # Label & next steps
        if final_score >= 70:
            label = "High Risk"
            next_steps = [
                "Do NOT click or visit this link",
                "Report at cybercrime.gov.in",
                "Call the cyber-crime helpline 1930",
                "Warn others in your contact list",
            ]
        elif final_score >= 40:
            label = "Suspicious"
            next_steps = [
                "Be cautious before clicking",
                "Verify the sender independently",
                "Visit the official website directly (do not follow this link)",
                "Report at cybercrime.gov.in if you are unsure",
            ]
        else:
            label = "Safe"
            if not reasons:
                reasons = ["No suspicious indicators detected"]
            next_steps = [
                "URL appears safe",
                "Always verify before sharing personal information",
            ]

        return {
            "risk_score": round(final_score, 1),
            "label": label,
            "reasons": reasons if reasons else ["No suspicious indicators detected"],
            "indicators": {
                "domain": full_domain,
                "subdomain": ext.subdomain or None,
                "tld": ext.suffix,
                "has_https": bool(feats["is_https"]),
                "lookalike_score": round(feats["lookalike_score"], 3),
            },
            "next_steps": next_steps,
            "signals": signals,
        }
