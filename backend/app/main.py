"""
FastAPI application entry point.
Mounts all routers and initialises models on startup.
"""

from __future__ import annotations

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.database import Base, engine
from app.ml.url_analyzer import URLAnalyzer
from app.ml.sms_classifier import SMSClassifier
from app.routers import campaigns, checker, dashboard, reports

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Fraud Shield API",
    description="Rajasthan Police Hackathon 2026 · PS01: Cyber Fraud · Team Dholakpurwale",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Startup ───────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup() -> None:
    Base.metadata.create_all(bind=engine)
    # Warm up ML models (they train lazily via singleton)
    URLAnalyzer.get_instance()
    SMSClassifier.get_instance()
    print("✅  Fraud Shield API ready – models loaded.")


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(checker.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# ── SSE Live Feed ─────────────────────────────────────────────────────────────

DISTRICTS = [
    "Jaipur", "Jodhpur", "Udaipur", "Bikaner", "Kota",
    "Ajmer", "Alwar", "Sikar", "Bharatpur", "Churu",
]
LIVE_EVENTS = [
    ("New report", "Phishing URL detected: sbi-kyc-update.xyz", "High Risk"),
    ("Campaign alert", "SBI KYC Scam cluster grew to 36 reports", "High Risk"),
    ("New report", "Fake electricity bill SMS from 9876543210", "High Risk"),
    ("New report", "Suspicious parcel customs SMS detected", "Suspicious"),
    ("Takedown", "Domain rto-challan-pay.xyz flagged for takedown", "High Risk"),
    ("New report", "Job scam WhatsApp forward detected", "Suspicious"),
    ("Campaign alert", "PhonePe cashback scam – 5 new reports", "High Risk"),
    ("New report", "Fake loan offer SMS intercepted", "Suspicious"),
    ("New report", "IRCTC lucky draw phishing link detected", "High Risk"),
    ("Campaign resolved", "Electricity bill scam campaign resolved", "Safe"),
    ("New report", "Legitimate SBI OTP message – Safe", "Safe"),
    ("New report", "UPI refund scam detected via keyword match", "High Risk"),
]


async def sse_generator():
    idx = 0
    while True:
        event_type, message, risk = LIVE_EVENTS[idx % len(LIVE_EVENTS)]
        district = random.choice(DISTRICTS)
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            "message": message,
            "district": district,
            "risk_level": risk,
        }
        yield f"data: {json.dumps(event)}\n\n"
        idx += 1
        await asyncio.sleep(3)


@app.get("/api/live-feed")
async def live_feed():
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── Static UI (Serves built frontend at http://localhost:8000) ───────────────

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DIST_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))

if os.path.exists(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept /api routes
        if full_path.startswith("api/"):
            return None
        file_path = os.path.join(DIST_DIR, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        index_file = os.path.join(DIST_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend build not found. Run 'npm run build' inside /frontend"}
