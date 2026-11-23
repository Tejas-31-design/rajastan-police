"""
Checker router — URL and SMS analysis endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.sms_classifier import SMSClassifier
from app.ml.url_analyzer import URLAnalyzer
from app.models import Report
from app.schemas import CheckResponse, CheckSMSRequest, CheckURLRequest

router = APIRouter(tags=["checker"])


@router.post("/check/url", response_model=CheckResponse)
def check_url(req: CheckURLRequest, db: Session = Depends(get_db)) -> CheckResponse:
    analyzer = URLAnalyzer.get_instance()
    result = analyzer.analyze(req.url)

    # Persist report
    report = Report(
        source_type="url",
        content=req.url,
        risk_score=result["risk_score"],
        label=result["label"],
        reasons=result["reasons"],
        indicators=result["indicators"],
        next_steps=result["next_steps"],
        signals=result["signals"],
        district="Unknown",
    )
    db.add(report)
    db.commit()

    return CheckResponse(**result)


@router.post("/check/sms", response_model=CheckResponse)
def check_sms(req: CheckSMSRequest, db: Session = Depends(get_db)) -> CheckResponse:
    classifier = SMSClassifier.get_instance()
    url_analyzer = URLAnalyzer.get_instance()
    result = classifier.analyze(req.text, url_analyzer=url_analyzer)

    # Persist report
    report = Report(
        source_type="sms",
        content=req.text,
        risk_score=result["risk_score"],
        label=result["label"],
        reasons=result["reasons"],
        indicators=result["indicators"],
        next_steps=result["next_steps"],
        signals=result["signals"],
        district="Unknown",
    )
    db.add(report)
    db.commit()

    return CheckResponse(**result)
