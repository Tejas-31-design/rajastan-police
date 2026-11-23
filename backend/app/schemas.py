from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime


# ── Check request/response ─────────────────────────────────────────────────────

class CheckURLRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2000)


class CheckSMSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class SignalItem(BaseModel):
    name: str
    weight: float
    triggered: bool


class CheckResponse(BaseModel):
    risk_score: float
    label: str
    reasons: List[str]
    indicators: Dict[str, Any]
    next_steps: List[str]
    signals: List[SignalItem]


# ── Campaign ──────────────────────────────────────────────────────────────────

class IndicatorOut(BaseModel):
    id: int
    type: str
    value: str
    report_count: int
    first_seen: datetime
    last_seen: datetime

    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: int
    created_at: datetime
    source_type: str
    content: str
    risk_score: float
    label: str
    reasons: List[str]
    indicators: Dict[str, Any]
    district: str
    campaign_id: Optional[int]

    model_config = {"from_attributes": True}


class CampaignSummary(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
    report_count: int
    risk_level: str
    status: str
    district: str
    description: str
    indicators: Dict[str, Any]

    model_config = {"from_attributes": True}


class GraphNode(BaseModel):
    id: str
    label: str
    type: str          # report | domain | phone | upi | sender
    risk_score: Optional[float] = None
    district: Optional[str] = None


class GraphLink(BaseModel):
    source: str
    target: str
    label: str


class CampaignGraph(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]


class CampaignDetail(BaseModel):
    campaign: CampaignSummary
    reports: List[ReportOut]
    indicators: List[IndicatorOut]
    graph: CampaignGraph
    timeline: List[Dict[str, Any]]


# ── Dashboard ─────────────────────────────────────────────────────────────────

class DashboardStats(BaseModel):
    reports_today: int
    active_campaigns: int
    high_risk_domains: int
    top_district: str
    total_reports: int
    resolved_campaigns: int


class TrendPoint(BaseModel):
    date: str
    reports: int
    high_risk: int


class DistrictHotspot(BaseModel):
    district: str
    lat: float
    lng: float
    count: int
    risk_level: str


class LiveEvent(BaseModel):
    id: str
    timestamp: datetime
    type: str
    message: str
    district: str
    risk_level: str
