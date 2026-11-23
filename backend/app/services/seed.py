"""
Seed generator — creates ~300 synthetic reports across 10 campaigns in Rajasthan.
Run with:  python -m app.services.seed
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

# Allow running as __main__
if __name__ == "__main__":
    import os, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from app.database import Base, SessionLocal, engine
from app.models import Campaign, Indicator, Report
from app.ml.clustering import rebuild_campaigns

random.seed(42)

DISTRICTS = [
    "Jaipur", "Jodhpur", "Udaipur", "Bikaner", "Kota",
    "Ajmer", "Alwar", "Sikar", "Bharatpur", "Churu",
    "Nagaur", "Barmer", "Jhalawar", "Tonk", "Pali",
]

# ── Campaign blueprints ────────────────────────────────────────────────────────

CAMPAIGNS: list[dict] = [
    {
        "theme": "SBI KYC Scam",
        "district": "Jaipur",
        "source_type": "sms",
        "domains": ["sbi-kyc-update.xyz", "sbi0nline.xyz"],
        "phones": ["9876543210", "9876543211"],
        "upis": [],
        "count": 35,
        "templates": [
            "Aapka SBI account block ho jayega 24 ghante mein. KYC update karein: http://sbi-kyc-update.xyz",
            "URGENT: Your SBI account is suspended. Complete KYC now at http://sbi-kyc-update.xyz or call 9876543210",
            "Dear SBI customer, your account access is blocked. Update KYC immediately: http://sbi0nline.xyz",
            "SBI Alert: KYC verification pending. Account will be blocked. Click: http://sbi-kyc-update.xyz",
            "SBI Bank notice: Aapka KYC expire ho gaya hai. Renew karein: http://sbi0nline.xyz",
        ],
        "risk_range": (75, 95),
    },
    {
        "theme": "Fake RTO Challan",
        "district": "Jodhpur",
        "source_type": "url",
        "domains": ["rto-challan-pay.xyz", "rto-echallan-rajasthan.top"],
        "phones": ["9988776655"],
        "upis": ["challanpay@upi"],
        "count": 28,
        "templates": [
            "Traffic challan pending. Pay online: http://rto-challan-pay.xyz",
            "RTO Rajasthan: Your vehicle MH14XX1234 has an unpaid challan. Pay Rs 500: http://rto-echallan-rajasthan.top",
            "Parivahan Sewa: Challan generated for vehicle. Pay: http://rto-challan-pay.xyz",
            "Rajasthan Police: Overspeed challan Rs 1000. Pay within 7 days: http://rto-echallan-rajasthan.top",
        ],
        "risk_range": (70, 90),
    },
    {
        "theme": "Electricity Bill Scam",
        "district": "Bikaner",
        "source_type": "sms",
        "domains": ["jvvnl-bill-pay.xyz", "discom-urgent-pay.top"],
        "phones": ["9123456789"],
        "upis": ["jvvnl@fake"],
        "count": 25,
        "templates": [
            "JVVNL: Aapka electricity connection aaj raat band ho jayega. Turant pay karein: http://jvvnl-bill-pay.xyz",
            "URGENT: Your electricity will be disconnected tonight. Pay Rs 1,240 now: http://discom-urgent-pay.top",
            "Bijli vibhag: Last warning. Meter band hoga 9 PM pe. Pay: http://jvvnl-bill-pay.xyz",
            "AVVNL notice: Unpaid bill. Connection cut tonight. Pay: 9123456789",
        ],
        "risk_range": (72, 92),
    },
    {
        "theme": "Parcel Customs Scam",
        "district": "Udaipur",
        "source_type": "sms",
        "domains": ["customs-parcel-release.xyz", "indiapost-parcel-hold.xyz"],
        "phones": ["9811223344"],
        "upis": [],
        "count": 22,
        "templates": [
            "India Post: Aapka parcel customs mein rok diya gaya. Rs 149 pay karein: http://customs-parcel-release.xyz",
            "Your Amazon package is held at customs. Pay duty Rs 299: http://customs-parcel-release.xyz",
            "DHL: International shipment on hold. Pay customs fee Rs 350: http://indiapost-parcel-hold.xyz",
            "FedEx: Package ID IN8827443 at customs. Pay Rs 199 to release: http://customs-parcel-release.xyz",
        ],
        "risk_range": (68, 88),
    },
    {
        "theme": "Fake Job Offer",
        "district": "Kota",
        "source_type": "sms",
        "domains": [],
        "phones": ["9123456789", "9876501234"],
        "upis": [],
        "count": 30,
        "templates": [
            "Work from home! Earn Rs 50,000/month. No experience needed. WhatsApp 9876501234",
            "Ghar baithe paise kamao. Rs 500 per hour data entry. Contact: 9123456789",
            "Part time job available. Rs 20,000-35,000/month. Online work. Call 9123456789",
            "Data entry job work from home. Earn Rs 15,000 weekly. Apply: 9876501234",
            "Genuine online job. No investment. Earn Rs 2000/day. WhatsApp 9123456789",
        ],
        "risk_range": (60, 82),
    },
    {
        "theme": "UPI Refund Scam",
        "district": "Ajmer",
        "source_type": "sms",
        "domains": ["upi-refund-claim.click"],
        "phones": [],
        "upis": ["refund@upi", "cashback@ybl"],
        "count": 20,
        "templates": [
            "PhonePe cashback Rs 5,000 pending. Claim via UPI: refund@upi. Click: http://upi-refund-claim.click",
            "Google Pay refund Rs 2,000 pending. Send request to: cashback@ybl immediately.",
            "Paytm cashback Rs 1,500 available. Scan QR or add UPI: refund@upi. Limited time!",
            "BHIM UPI refund Rs 3,000 from last transaction. Claim at: http://upi-refund-claim.click",
        ],
        "risk_range": (70, 90),
    },
    {
        "theme": "Fake Loan Offer",
        "district": "Sikar",
        "source_type": "sms",
        "domains": ["loan-offer-instant.xyz"],
        "phones": ["9988001122"],
        "upis": [],
        "count": 18,
        "templates": [
            "Instant personal loan Rs 5 lakh in 30 minutes! No documents. WhatsApp 9988001122",
            "Pre-approved loan Rs 3 lakh at 0% interest. Apply: http://loan-offer-instant.xyz",
            "Govt scheme: Rs 10 lakh loan without guarantor. Apply now: 9988001122",
            "Aadhar se turant loan Rs 2 lakh. Bina document ke. Click: http://loan-offer-instant.xyz",
        ],
        "risk_range": (65, 85),
    },
    {
        "theme": "IRCTC Reward Scam",
        "district": "Alwar",
        "source_type": "url",
        "domains": ["irctc-lucky-draw.top"],
        "phones": ["9871234560"],
        "upis": [],
        "count": 24,
        "templates": [
            "IRCTC lucky draw winner! Claim free train ticket: http://irctc-lucky-draw.top",
            "Congratulations! You won IRCTC reward Rs 1 lakh. Claim: http://irctc-lucky-draw.top",
            "IRCTC: Aap lucky draw mein jeete! Prize claim: http://irctc-lucky-draw.top. Call 9871234560",
        ],
        "risk_range": (72, 92),
    },
    {
        "theme": "PhonePe Cashback Scam",
        "district": "Bharatpur",
        "source_type": "url",
        "domains": ["phonepe-cashback-offer.xyz"],
        "phones": [],
        "upis": ["cashback@phonepe-fake"],
        "count": 20,
        "templates": [
            "PhonePe Diwali offer! Rs 5000 cashback. Claim: http://phonepe-cashback-offer.xyz",
            "PhonePe anniversary reward! Scan QR and get Rs 2000. Click: http://phonepe-cashback-offer.xyz",
            "Special PhonePe cashback pending. Add UPI: cashback@phonepe-fake to claim.",
        ],
        "risk_range": (70, 88),
    },
    {
        "theme": "India Post Package Scam",
        "district": "Churu",
        "source_type": "sms",
        "domains": ["indiapost-parcel-hold.xyz"],
        "phones": ["9900112233"],
        "upis": [],
        "count": 18,
        "templates": [
            "India Post: Package held at Churu depot. Pay Rs 89 delivery fee: http://indiapost-parcel-hold.xyz",
            "India Post notice: Aapka parcel depot mein hai. Rs 89 pay karein: 9900112233",
            "Your India Post package could not be delivered. Pay Rs 50 redelivery fee: http://indiapost-parcel-hold.xyz",
        ],
        "risk_range": (65, 85),
    },
]

# Safe reports
SAFE_TEMPLATES = [
    ("Your OTP for SBI Net Banking is {otp}. Valid for 10 minutes. Do NOT share with anyone.", "sms"),
    ("Transaction Alert: Rs {amount} debited from HDFC A/c XX4521. Bal Rs {bal}. If not done call 18002586161.", "sms"),
    ("Your Flipkart order #{order_id} has been shipped. Expected delivery: {date}. Track at flipkart.com", "sms"),
    ("IRCTC: PNR {pnr} confirmed. Train {train}. Coach S3 Seat {seat}. Depart {time}.", "sms"),
    ("Jio: Your monthly recharge Rs 299 successful. Validity 28 days. Data: 1.5 GB/day.", "sms"),
    ("https://www.sbi.co.in", "url"),
    ("https://www.hdfcbank.com", "url"),
    ("https://www.paytm.com", "url"),
    ("https://irctc.co.in", "url"),
    ("https://rajasthan.gov.in", "url"),
    ("https://cybercrime.gov.in", "url"),
    ("https://www.amazon.in", "url"),
    ("https://www.flipkart.com", "url"),
    ("https://www.phonepe.com", "url"),
    ("https://www.google.com", "url"),
]


def _random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def _make_report(template: str, source_type: str, risk_score: float, district: str,
                 domains: list[str], phones: list[str], upis: list[str], label: str) -> dict:
    # Pick a random indicator to embed
    domain = random.choice(domains) if domains else None
    phone = random.choice(phones) if phones else None
    upi = random.choice(upis) if upis else None

    # Build reasons based on risk
    reasons: list[str] = []
    if label == "High Risk":
        if domain:
            reasons.append(f"Suspicious domain: {domain}")
        reasons.append("Suspicious TLD detected (.xyz, .top, .click)")
        reasons.append("Contains scam keywords (kyc, verify, block, claim)")
        if phone:
            reasons.append(f"Phone number extracted: {phone}")
        if upi:
            reasons.append(f"UPI ID extracted: {upi}")
    elif label == "Suspicious":
        reasons.append("Contains suspicious patterns")
        if domain:
            reasons.append(f"Unverified domain: {domain}")
    else:
        reasons = ["No suspicious indicators detected"]

    indicators: dict = {}
    if domain:
        indicators["domain"] = domain
    if phones:
        indicators["phones"] = [p for p in phones if p]
    if upis:
        indicators["upis"] = [u for u in upis if u]

    return {
        "content": template,
        "source_type": source_type,
        "risk_score": risk_score,
        "label": label,
        "reasons": reasons,
        "indicators": indicators,
        "next_steps": [
            "Do NOT click or respond",
            "Report at cybercrime.gov.in",
            "Call 1930",
        ] if label != "Safe" else [
            "Message appears safe",
            "Always verify before sharing information",
        ],
        "signals": [],
        "district": district,
    }


def seed_database(db: Session) -> None:
    print("Seeding database with synthetic data...")
    now = datetime.utcnow()
    start_date = now - timedelta(days=90)

    all_reports: list[dict] = []

    # Scam campaigns
    for camp in CAMPAIGNS:
        for i in range(camp["count"]):
            template = random.choice(camp["templates"])
            # Slight text variation
            if "{" not in template:
                variation_suffix = random.choice(["", " Act now!", " Last chance.", " Ignore at your risk."])
                content = template + variation_suffix if random.random() > 0.5 else template
            else:
                content = template
            risk_score = round(random.uniform(*camp["risk_range"]), 1)
            label = "High Risk" if risk_score >= 70 else "Suspicious"
            district = camp["district"] if random.random() > 0.3 else random.choice(DISTRICTS[:8])

            rpt = _make_report(
                content, camp["source_type"], risk_score, district,
                camp["domains"], camp["phones"], camp["upis"], label,
            )
            rpt["created_at"] = _random_date(start_date, now)
            all_reports.append(rpt)

    # Safe reports
    for template, source_type in SAFE_TEMPLATES:
        content = template.format(
            otp=random.randint(100000, 999999),
            amount=random.randint(100, 10000),
            bal=random.randint(1000, 50000),
            order_id=f"OD{random.randint(100000, 999999)}",
            date=(now + timedelta(days=random.randint(1, 7))).strftime("%d %b"),
            pnr=random.randint(1000000000, 9999999999),
            train=f"{random.randint(10000, 99999)}",
            seat=random.randint(1, 72),
            time=f"{random.randint(6, 22):02d}:{random.choice(['00','15','30','45'])}",
        )
        rpt = _make_report(content, source_type, random.uniform(5, 25), random.choice(DISTRICTS), [], [], [], "Safe")
        rpt["created_at"] = _random_date(start_date, now)
        all_reports.append(rpt)

    # Shuffle for realistic order
    random.shuffle(all_reports)

    # Bulk insert reports
    report_objs: list[Report] = []
    for r in all_reports:
        obj = Report(
            created_at=r["created_at"],
            source_type=r["source_type"],
            content=r["content"],
            risk_score=r["risk_score"],
            label=r["label"],
            reasons=r["reasons"],
            indicators=r["indicators"],
            next_steps=r["next_steps"],
            signals=r["signals"],
            district=r["district"],
        )
        report_objs.append(obj)

    db.add_all(report_objs)
    db.commit()

    print(f"✅  Inserted {len(report_objs)} synthetic reports.")
    print("🔗  Running clustering engine...")
    rebuild_campaigns(db)

    camp_count = db.query(Campaign).count()
    print(f"✅  Created {camp_count} campaigns.")
    print("🌱  Seed complete!")


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Indicator).delete()
        db.query(Report).delete()
        db.query(Campaign).delete()
        db.commit()
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
