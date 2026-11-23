"""
Campaigns router — list, detail, graph, and PDF export.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.clustering import build_campaign_graph
from app.models import Campaign, Indicator, Report
from app.schemas import CampaignDetail, CampaignGraph, CampaignSummary
from app.services.pdf_export import generate_evidence_pdf

router = APIRouter(tags=["campaigns"])


@router.get("/campaigns", response_model=list[CampaignSummary])
def list_campaigns(db: Session = Depends(get_db)) -> list[CampaignSummary]:
    camps = (
        db.query(Campaign)
        .order_by(Campaign.report_count.desc())
        .all()
    )
    return [CampaignSummary.model_validate(c) for c in camps]


@router.get("/campaigns/{campaign_id}", response_model=CampaignDetail)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)) -> CampaignDetail:
    camp = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    rpts = db.query(Report).filter(Report.campaign_id == campaign_id).all()
    inds = db.query(Indicator).filter(Indicator.campaign_id == campaign_id).all()

    graph_data = build_campaign_graph(camp, rpts, inds)

    # Build timeline
    timeline = []
    for r in sorted(rpts, key=lambda x: x.created_at):
        timeline.append({
            "date": r.created_at.isoformat(),
            "event": f"Report #{r.id}: {r.label} ({r.risk_score})",
            "district": r.district,
            "risk_level": r.label,
        })

    return CampaignDetail(
        campaign=CampaignSummary.model_validate(camp),
        reports=[
            {
                "id": r.id,
                "created_at": r.created_at,
                "source_type": r.source_type,
                "content": r.content,
                "risk_score": r.risk_score,
                "label": r.label,
                "reasons": r.reasons or [],
                "indicators": r.indicators or {},
                "district": r.district or "Unknown",
                "campaign_id": r.campaign_id,
            }
            for r in rpts
        ],
        indicators=[
            {
                "id": ind.id,
                "type": ind.type,
                "value": ind.value,
                "report_count": ind.report_count,
                "first_seen": ind.first_seen,
                "last_seen": ind.last_seen,
            }
            for ind in inds
        ],
        graph=CampaignGraph(**graph_data),
        timeline=timeline,
    )


@router.get("/campaigns/{campaign_id}/export-pdf")
def export_pdf(campaign_id: int, db: Session = Depends(get_db)) -> Response:
    camp = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    rpts = db.query(Report).filter(Report.campaign_id == campaign_id).all()
    inds = db.query(Indicator).filter(Indicator.campaign_id == campaign_id).all()

    pdf_bytes = generate_evidence_pdf(camp, rpts, inds)
    safe_name = camp.name.replace(" ", "_").replace("/", "-")[:50]

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="FraudShield_Evidence_{safe_name}.pdf"'
        },
    )
