"""
Campaign clustering engine.

Builds a graph of reports linked by shared indicators (domain, phone, UPI, sender).
Connected components become campaigns.
Reworded SMS variants are merged when TF-IDF cosine similarity ≥ 0.7.
"""

from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.models import Campaign, Indicator, Report

COSINE_THRESHOLD = 0.70


def _extract_indicator_key(report: Report) -> list[tuple[str, str]]:
    """Return (type, value) pairs for all indicators in a report."""
    keys: list[tuple[str, str]] = []
    ind: dict = report.indicators or {}

    if domain := ind.get("domain"):
        keys.append(("domain", domain.lower()))
    for phone in ind.get("phones", []):
        keys.append(("phone", phone.strip()))
    for upi in ind.get("upis", []):
        keys.append(("upi", upi.lower()))
    for sender in ind.get("senders", []):
        keys.append(("sender", sender.lower()))
    return keys


def _auto_name(reports: list[Report], campaign_id: int) -> str:
    """Generate a human-readable campaign name from report signals."""
    districts = [r.district for r in reports if r.district]
    top_district = max(set(districts), key=districts.count) if districts else "Rajasthan"

    # Guess theme from reasons
    all_reasons = " ".join(
        " ".join(r.reasons or []) for r in reports
    ).lower()

    if "kyc" in all_reasons or "account block" in all_reasons:
        theme = "KYC / Account Block"
    elif "challan" in all_reasons or "rto" in all_reasons:
        theme = "Fake RTO Challan"
    elif "electricity" in all_reasons or "bijli" in all_reasons:
        theme = "Electricity Bill"
    elif "parcel" in all_reasons or "customs" in all_reasons:
        theme = "Parcel Customs"
    elif "job" in all_reasons or "work from home" in all_reasons:
        theme = "Fake Job Offer"
    elif "loan" in all_reasons:
        theme = "Fake Loan"
    elif "lottery" in all_reasons or "prize" in all_reasons or "lucky" in all_reasons:
        theme = "Fake Lottery / Prize"
    elif "upi" in all_reasons or "cashback" in all_reasons:
        theme = "UPI Refund"
    elif "irctc" in all_reasons:
        theme = "IRCTC Reward"
    else:
        theme = f"Scam Campaign #{campaign_id}"

    # Try to get brand from domains
    domains: list[str] = []
    for r in reports:
        if d := (r.indicators or {}).get("domain"):
            domains.append(d)
    brand = ""
    brand_map = {
        "sbi": "SBI", "hdfc": "HDFC", "icici": "ICICI",
        "paytm": "Paytm", "phonepe": "PhonePe",
        "irctc": "IRCTC", "rto": "RTO", "jvvnl": "JVVNL",
        "india": "India Post",
    }
    for d in domains:
        for key, label in brand_map.items():
            if key in d:
                brand = label + " "
                break
        if brand:
            break

    return f"{brand}{theme} – {top_district} Cluster"


def rebuild_campaigns(db: Session) -> None:
    """
    Rebuild all campaigns from scratch using graph clustering.
    Should be called after bulk seed. For incremental use add_report_to_cluster().
    """
    # Clear existing campaign assignments (keep campaigns for now)
    all_reports: list[Report] = db.query(Report).all()

    if not all_reports:
        return

    # --- Build indicator graph ---
    G = nx.Graph()
    for r in all_reports:
        G.add_node(f"R{r.id}", report=r)

    # Connect reports that share indicators
    indicator_index: dict[tuple[str, str], list[int]] = {}
    for r in all_reports:
        for ind_type, ind_value in _extract_indicator_key(r):
            key = (ind_type, ind_value)
            indicator_index.setdefault(key, []).append(r.id)

    for (ind_type, ind_value), report_ids in indicator_index.items():
        for i in range(len(report_ids)):
            for j in range(i + 1, len(report_ids)):
                G.add_edge(f"R{report_ids[i]}", f"R{report_ids[j]}",
                           label=f"{ind_type}:{ind_value}")

    # --- SMS text similarity merge ---
    sms_reports = [r for r in all_reports if r.source_type == "sms" and r.content]
    if len(sms_reports) >= 2:
        texts = [r.content for r in sms_reports]
        try:
            vec = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
            tfidf_matrix = vec.fit_transform(texts)
            sim_matrix = cosine_similarity(tfidf_matrix)
            for i in range(len(sms_reports)):
                for j in range(i + 1, len(sms_reports)):
                    if sim_matrix[i, j] >= COSINE_THRESHOLD:
                        G.add_edge(
                            f"R{sms_reports[i].id}",
                            f"R{sms_reports[j].id}",
                            label="text_similar",
                        )
        except Exception:
            pass

    # --- Connected components → campaigns ---
    # Remove old data
    db.query(Indicator).delete()
    db.query(Campaign).delete()
    db.flush()

    components = list(nx.connected_components(G))

    for comp in components:
        report_nodes = [n for n in comp if n.startswith("R")]
        comp_reports = [r for r in all_reports if f"R{r.id}" in report_nodes]

        if not comp_reports:
            continue

        # Only create a campaign if there are multiple reports or at least one High Risk
        high_risk = any(r.label == "High Risk" for r in comp_reports)
        if len(comp_reports) < 2 and not high_risk:
            continue

        # Determine risk level
        scores = [r.risk_score for r in comp_reports]
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score >= 70:
            risk_level = "High"
        elif avg_score >= 40:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Top district
        districts = [r.district for r in comp_reports if r.district]
        top_district = max(set(districts), key=districts.count) if districts else "Rajasthan"

        # Collect all indicators for this campaign
        camp_indicators: dict[str, list[str]] = {
            "domains": [], "phones": [], "upis": [], "senders": [],
        }
        for r in comp_reports:
            ind = r.indicators or {}
            if d := ind.get("domain"):
                camp_indicators["domains"].append(d)
            camp_indicators["phones"].extend(ind.get("phones", []))
            camp_indicators["upis"].extend(ind.get("upis", []))
            camp_indicators["senders"].extend(ind.get("senders", []))
        # Deduplicate
        camp_indicators = {k: list(dict.fromkeys(v)) for k, v in camp_indicators.items()}

        created_at = min(r.created_at for r in comp_reports)
        updated_at = max(r.created_at for r in comp_reports)

        temp_name = _auto_name(comp_reports, 0)
        camp = Campaign(
            name=temp_name,
            report_count=len(comp_reports),
            risk_level=risk_level,
            indicators=camp_indicators,
            status="active" if high_risk else "monitoring",
            district=top_district,
            description=f"Auto-detected cluster of {len(comp_reports)} related reports.",
            created_at=created_at,
            updated_at=updated_at,
        )
        db.add(camp)
        db.flush()

        # Refine name with ID
        camp.name = _auto_name(comp_reports, camp.id)

        # Assign reports to campaign
        for r in comp_reports:
            r.campaign_id = camp.id

        # Create indicator records
        for ind_type, ind_values in camp_indicators.items():
            singular = ind_type.rstrip("s")  # domains→domain, phones→phone
            for val in ind_values[:20]:  # cap at 20 per type
                ind_rec = Indicator(
                    type=singular,
                    value=val,
                    report_count=sum(
                        1 for r in comp_reports
                        if val in str((r.indicators or {}).get(ind_type, []))
                        or val == (r.indicators or {}).get("domain")
                    ),
                    campaign_id=camp.id,
                    first_seen=created_at,
                    last_seen=updated_at,
                )
                db.add(ind_rec)

    db.commit()


def build_campaign_graph(campaign: Campaign, reports: list[Report], indicators: list[Indicator]) -> dict[str, Any]:
    """Build force-graph node/link structure for a campaign."""
    nodes: list[dict] = []
    links: list[dict] = []
    seen_nodes: set[str] = set()

    def add_node(node_id: str, label: str, node_type: str, **kwargs: Any) -> None:
        if node_id not in seen_nodes:
            nodes.append({"id": node_id, "label": label, "type": node_type, **kwargs})
            seen_nodes.add(node_id)

    # Report nodes
    for r in reports:
        node_id = f"report_{r.id}"
        add_node(
            node_id,
            f"Report #{r.id}",
            "report",
            risk_score=r.risk_score,
            district=r.district,
            label_risk=r.label,
        )

    # Indicator nodes and links
    for ind in indicators:
        ind_id = f"{ind.type}_{ind.value}"
        type_labels = {
            "domain": "🌐", "phone": "📞", "upi": "💸", "sender": "📱",
        }
        prefix = type_labels.get(ind.type, "•")
        add_node(ind_id, f"{prefix} {ind.value}", ind.type, report_count=ind.report_count)

        # Link reports to this indicator
        for r in reports:
            ind_data = r.indicators or {}
            report_values = (
                [ind_data.get("domain")]
                + ind_data.get("phones", [])
                + ind_data.get("upis", [])
                + ind_data.get("senders", [])
            )
            report_values = [v for v in report_values if v]
            if ind.value in report_values:
                links.append({
                    "source": f"report_{r.id}",
                    "target": ind_id,
                    "label": ind.type,
                })

    return {"nodes": nodes, "links": links}
