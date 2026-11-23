"""
Evidence PDF generator using ReportLab.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Colour palette matching the UI
NAVY = colors.HexColor("#0B1B2B")
CARD = colors.HexColor("#12304D")
SAFFRON = colors.HexColor("#F28C28")
TEAL = colors.HexColor("#0FA3A3")
RED = colors.HexColor("#D64545")
GREEN = colors.HexColor("#22C55E")
WHITE = colors.white
LIGHT_GREY = colors.HexColor("#D1D5DB")

PAGE_W, PAGE_H = A4


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"],
            fontSize=20, textColor=SAFFRON, spaceAfter=4,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=11, textColor=TEAL, spaceAfter=2,
            alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "section", parent=base["Heading2"],
            fontSize=13, textColor=SAFFRON,
            fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=9, textColor=colors.black, leading=14,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"],
            fontSize=8, textColor=colors.grey,
        ),
        "chip_high": ParagraphStyle(
            "chip_high", parent=base["Normal"],
            fontSize=8, textColor=WHITE, backColor=RED,
        ),
        "chip_safe": ParagraphStyle(
            "chip_safe", parent=base["Normal"],
            fontSize=8, textColor=WHITE, backColor=GREEN,
        ),
        "mono": ParagraphStyle(
            "mono", parent=base["Code"],
            fontSize=8, leading=12,
        ),
    }


def _risk_color(label: str) -> colors.Color:
    return {
        "High Risk": RED,
        "Suspicious": SAFFRON,
        "Safe": GREEN,
    }.get(label, TEAL)


def generate_evidence_pdf(
    campaign: Any,
    reports: list[Any],
    indicators: list[Any],
) -> bytes:
    """Generate a ReportLab PDF evidence report and return bytes."""
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Evidence Report – {campaign.name}",
        author="Fraud Shield · Rajasthan Police Hackathon 2026",
    )

    styles = _styles()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("🛡️  FRAUD SHIELD", styles["title"]))
    story.append(Paragraph("Cyber Fraud Evidence Report", styles["subtitle"]))
    story.append(Paragraph(
        "⚠️  SYNTHETIC DEMO DATA — For demonstration purposes only",
        ParagraphStyle("warn", fontSize=8, textColor=RED, alignment=TA_CENTER),
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=SAFFRON))
    story.append(Spacer(1, 0.3 * cm))

    # ── Campaign Overview ─────────────────────────────────────────────────────
    story.append(Paragraph("CAMPAIGN OVERVIEW", styles["section"]))
    overview_data = [
        ["Campaign Name", campaign.name],
        ["Status", campaign.status.upper()],
        ["Risk Level", campaign.risk_level],
        ["Total Reports", str(campaign.report_count)],
        ["Primary District", campaign.district],
        ["First Seen", campaign.created_at.strftime("%d %b %Y %H:%M UTC")],
        ["Last Updated", campaign.updated_at.strftime("%d %b %Y %H:%M UTC")],
        ["Report Generated", datetime.utcnow().strftime("%d %b %Y %H:%M UTC")],
    ]
    overview_table = Table(overview_data, colWidths=[5 * cm, 11 * cm])
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), CARD),
        ("TEXTCOLOR", (0, 0), (0, -1), SAFFRON),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.black),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GREY]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── Indicators ────────────────────────────────────────────────────────────
    story.append(Paragraph("INDICATORS OF COMPROMISE", styles["section"]))
    if indicators:
        ind_data = [["Type", "Value", "Report Count", "First Seen"]]
        for ind in indicators[:30]:
            ind_data.append([
                ind.type.upper(),
                ind.value[:45] + ("…" if len(ind.value) > 45 else ""),
                str(ind.report_count),
                ind.first_seen.strftime("%d %b %Y") if ind.first_seen else "—",
            ])
        ind_table = Table(ind_data, colWidths=[2.5 * cm, 9 * cm, 2.5 * cm, 3 * cm])
        ind_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), SAFFRON),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(ind_table)
    else:
        story.append(Paragraph("No indicators recorded.", styles["body"]))
    story.append(Spacer(1, 0.4 * cm))

    # ── Report Sample ─────────────────────────────────────────────────────────
    story.append(Paragraph("REPORT SAMPLE (up to 20)", styles["section"]))
    sample_reports = sorted(reports, key=lambda r: r.risk_score, reverse=True)[:20]

    if sample_reports:
        rep_data = [["#", "Date", "Type", "Score", "Label", "District", "Content (truncated)"]]
        for r in sample_reports:
            rep_data.append([
                str(r.id),
                r.created_at.strftime("%d/%m/%y") if r.created_at else "—",
                r.source_type.upper(),
                str(r.risk_score),
                r.label,
                r.district or "—",
                (r.content or "")[:50] + "…",
            ])
        rep_table = Table(
            rep_data,
            colWidths=[1 * cm, 1.8 * cm, 1.2 * cm, 1.2 * cm, 2 * cm, 2 * cm, 7.8 * cm],
        )
        rep_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), SAFFRON),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        # Colour code label column
        for i, r in enumerate(sample_reports, start=1):
            col = _risk_color(r.label)
            rep_table.setStyle(TableStyle([
                ("TEXTCOLOR", (4, i), (4, i), col),
                ("FONTNAME", (4, i), (4, i), "Helvetica-Bold"),
            ]))
        story.append(rep_table)
    else:
        story.append(Paragraph("No reports found.", styles["body"]))

    story.append(Spacer(1, 0.6 * cm))

    # ── Graph Adjacency ───────────────────────────────────────────────────────
    story.append(Paragraph("CAMPAIGN GRAPH (Adjacency Summary)", styles["section"]))
    story.append(Paragraph(
        "The following shared indicators link reports in this campaign. "
        "Full interactive graph available in the Fraud Shield dashboard.",
        styles["small"],
    ))
    story.append(Spacer(1, 0.2 * cm))
    ind_summary: dict[str, list[str]] = {}
    for ind in indicators:
        ind_summary.setdefault(ind.type, []).append(ind.value)
    for ind_type, values in ind_summary.items():
        story.append(Paragraph(
            f"<b>{ind_type.upper()}:</b> {', '.join(values[:8])}{'…' if len(values) > 8 else ''}",
            styles["body"],
        ))

    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GREY))
    story.append(Spacer(1, 0.2 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "Generated by Fraud Shield · Team Dholakpurwale · MIT Academy of Engineering",
        ParagraphStyle("footer", fontSize=7, textColor=colors.grey, alignment=TA_CENTER),
    ))
    story.append(Paragraph(
        "Rajasthan Police Hackathon 2026 · PS01: Cyber Fraud · All data is SYNTHETIC",
        ParagraphStyle("footer2", fontSize=7, textColor=colors.grey, alignment=TA_CENTER),
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()
