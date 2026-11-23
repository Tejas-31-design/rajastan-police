"""
Dashboard router — KPIs, trend, hotspot map.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, Report
from app.schemas import DashboardStats, DistrictHotspot, TrendPoint

router = APIRouter(tags=["dashboard"])

# Approximate Rajasthan district centroids [lat, lng]
DISTRICT_CENTROIDS: dict[str, tuple[float, float]] = {
    "Jaipur":    (26.9124, 75.7873),
    "Jodhpur":   (26.2389, 73.0243),
    "Udaipur":   (24.5854, 73.7125),
    "Bikaner":   (28.0229, 73.3119),
    "Kota":      (25.2138, 75.8648),
    "Ajmer":     (26.4499, 74.6399),
    "Alwar":     (27.5665, 76.6190),
    "Sikar":     (27.6094, 75.1399),
    "Bharatpur": (27.2152, 77.4938),
    "Churu":     (28.2960, 74.9589),
    "Nagaur":    (27.2024, 73.7360),
    "Barmer":    (25.7521, 71.3967),
    "Jhalawar":  (24.5979, 76.1620),
    "Tonk":      (26.1663, 75.7885),
    "Pali":      (25.7711, 73.3233),
    "Sirohi":    (24.8858, 72.8630),
    "Jaisalmer": (26.9157, 70.9083),
    "Dungarpur": (23.8428, 73.7147),
    "Bundi":     (25.4383, 75.6383),
    "Sawai Madhopur": (26.0193, 76.3540),
    "Dausa":     (26.8869, 76.3390),
    "Hanumangarh": (29.5831, 74.3292),
    "Ganganagar": (29.9220, 73.8771),
    "Dholpur":   (26.7006, 77.8891),
    "Karauli":   (26.5050, 77.0188),
    "Rajsamand": (25.0699, 73.8810),
    "Unknown":   (26.5, 74.5),  # Centre of Rajasthan
}


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)) -> DashboardStats:
    today = datetime.utcnow().date()
    today_start = datetime(today.year, today.month, today.day)

    reports_today = db.query(Report).filter(Report.created_at >= today_start).count()
    active_campaigns = db.query(Campaign).filter(Campaign.status == "active").count()
    resolved_campaigns = db.query(Campaign).filter(Campaign.status != "active").count()
    total_reports = db.query(Report).count()

    # High-risk domains
    all_reports = db.query(Report).filter(Report.label == "High Risk").all()
    domains: set[str] = set()
    for r in all_reports:
        if d := (r.indicators or {}).get("domain"):
            domains.add(d)
    high_risk_domains = len(domains)

    # Top district
    district_counts: Counter = Counter()
    for r in db.query(Report).filter(Report.label == "High Risk").all():
        if r.district and r.district != "Unknown":
            district_counts[r.district] += 1
    top_district = district_counts.most_common(1)[0][0] if district_counts else "Jaipur"

    return DashboardStats(
        reports_today=reports_today,
        active_campaigns=active_campaigns,
        high_risk_domains=high_risk_domains,
        top_district=top_district,
        total_reports=total_reports,
        resolved_campaigns=resolved_campaigns,
    )


@router.get("/dashboard/trend", response_model=list[TrendPoint])
def dashboard_trend(db: Session = Depends(get_db)) -> list[TrendPoint]:
    end = datetime.utcnow()
    start = end - timedelta(days=14)

    reports = (
        db.query(Report)
        .filter(Report.created_at >= start)
        .all()
    )

    daily: dict[str, dict[str, int]] = defaultdict(lambda: {"reports": 0, "high_risk": 0})
    for r in reports:
        day = r.created_at.strftime("%Y-%m-%d")
        daily[day]["reports"] += 1
        if r.label == "High Risk":
            daily[day]["high_risk"] += 1

    result = []
    for i in range(14):
        d = (start + timedelta(days=i)).strftime("%Y-%m-%d")
        result.append(TrendPoint(
            date=d,
            reports=daily[d]["reports"],
            high_risk=daily[d]["high_risk"],
        ))
    return result


@router.get("/dashboard/hotspots", response_model=list[DistrictHotspot])
def hotspots(db: Session = Depends(get_db)) -> list[DistrictHotspot]:
    reports = db.query(Report).filter(Report.district != None).all()
    district_data: dict[str, dict] = defaultdict(
        lambda: {"count": 0, "high_risk": 0}
    )
    for r in reports:
        if r.district:
            district_data[r.district]["count"] += 1
            if r.label == "High Risk":
                district_data[r.district]["high_risk"] += 1

    result = []
    for district, data in district_data.items():
        lat, lng = DISTRICT_CENTROIDS.get(district, DISTRICT_CENTROIDS["Unknown"])
        count = data["count"]
        high = data["high_risk"]
        risk_level = "High" if high / max(count, 1) > 0.5 else ("Medium" if high > 0 else "Low")
        result.append(DistrictHotspot(
            district=district,
            lat=lat,
            lng=lng,
            count=count,
            risk_level=risk_level,
        ))

    return sorted(result, key=lambda x: x.count, reverse=True)
