"""
Indian brand names used for lookalike / typosquat detection.
All entries are lowercased domain keywords.
"""

INDIAN_BRANDS = [
    # Banks
    "sbi", "sbionline", "onlinesbi",
    "hdfc", "hdfcbank",
    "icici", "icicibank",
    "axis", "axisbank",
    "kotak", "kotakbank",
    "pnb", "punjabbank",
    "bankofbaroda", "bobibank",
    "canarabank",
    "unionbank",
    # Payments
    "paytm",
    "phonepe",
    "googlepay", "gpay",
    "bhim",
    "amazonpay",
    "mobikwik",
    # Government / Public
    "irctc",
    "indiapost",
    "rto",
    "bsnl",
    "uidai", "aadhar", "aadhaar",
    "incometax",
    "gstn", "gst",
    "epfo",
    "nsc", "nationalsavings",
    "rajasthan",
    "cybercrime",
    # Telecoms
    "jio", "reliancejio",
    "airtel", "bhartiairtel",
    "vodafone", "vi",
    "bsnl",
    # E-commerce / Others
    "amazon", "flipkart", "snapdeal",
    "olacabs", "uber",
    "zomato", "swiggy",
]

# Domains known to be legitimate (zero lookalike risk)
SAFE_DOMAINS = {
    "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "paytm.com", "phonepe.com", "irctc.co.in",
    "indiapost.gov.in", "bsnl.co.in", "jio.com", "airtel.in",
    "amazon.in", "flipkart.com", "google.com", "govt.in",
    "rajasthan.gov.in", "cybercrime.gov.in", "incometax.gov.in",
}

# Simulated domain age table (days since registration)
DOMAIN_AGE_TABLE: dict[str, int] = {
    # Phishing domains — very new
    "sbi-kyc-update.xyz": 12,
    "sbi0nline.xyz": 7,
    "sbionline-secure.top": 5,
    "hdfc-verify-account.top": 8,
    "hdfc-kyc-update.click": 4,
    "paytm-reward-claim.click": 3,
    "paytm-cashback-win.xyz": 6,
    "rto-challan-pay.xyz": 14,
    "rto-echallan-rajasthan.top": 9,
    "jvvnl-bill-pay.xyz": 11,
    "discom-urgent-pay.top": 7,
    "customs-parcel-release.xyz": 15,
    "irctc-lucky-draw.top": 10,
    "phonepe-cashback-offer.xyz": 5,
    "indiapost-parcel-hold.xyz": 8,
    "loan-offer-instant.xyz": 13,
    "job-offer-wfh.top": 6,
    "upi-refund-claim.click": 4,
    # Legitimate domains — well-established
    "sbi.co.in": 9000,
    "hdfcbank.com": 8500,
    "icicibank.com": 7000,
    "paytm.com": 5000,
    "phonepe.com": 4000,
    "irctc.co.in": 8000,
    "google.com": 10000,
    "amazon.in": 6000,
    "flipkart.com": 5500,
    "rajasthan.gov.in": 6000,
    "cybercrime.gov.in": 3000,
}

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".click", ".work", ".loan", ".win",
    ".gq", ".ml", ".cf", ".tk", ".buzz", ".site", ".online",
    ".club", ".info", ".biz", ".pw", ".cc", ".su",
}

SUSPICIOUS_KEYWORDS = [
    "kyc", "verify", "update", "reward", "refund", "challan",
    "otp", "claim", "prize", "win", "expire", "block", "suspend",
    "urgent", "account", "login", "secure", "confirm", "authenticate",
    "password", "credential", "free", "congratulation", "lucky",
    "customs", "parcel", "job", "income", "earn",
]
