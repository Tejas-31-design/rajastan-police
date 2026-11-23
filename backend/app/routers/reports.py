"""
Reports router — list and detail.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Report
from app.schemas import ReportOut

router = APIRouter(tags=["reports"])


@router.get("/reports", response_model=list[ReportOut])
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    label: str | None = None,
    district: str | None = None,
    db: Session = Depends(get_db),
) -> list[ReportOut]:
    q = db.query(Report)
    if label:
        q = q.filter(Report.label == label)
    if district:
        q = q.filter(Report.district == district)
    rpts = q.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return [ReportOut.model_validate(r) for r in rpts]


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)) -> ReportOut:
    from fastapi import HTTPException
    r = db.query(Report).filter(Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportOut.model_validate(r)
