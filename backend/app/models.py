from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    report_count = Column(Integer, default=0)
    risk_level = Column(String, default="High")
    indicators = Column(JSON, default=dict)
    status = Column(String, default="active")
    district = Column(String, default="Jaipur")
    description = Column(Text, default="")

    reports = relationship("Report", back_populates="campaign", cascade="all, delete-orphan")
    indicators_list = relationship("Indicator", back_populates="campaign", cascade="all, delete-orphan")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    source_type = Column(String, default="url")  # url | sms | apk
    content = Column(Text, nullable=False)
    risk_score = Column(Float, default=0.0)
    label = Column(String, default="Safe")
    reasons = Column(JSON, default=list)
    indicators = Column(JSON, default=dict)
    next_steps = Column(JSON, default=list)
    signals = Column(JSON, default=list)
    district = Column(String, default="Jaipur")
    reporter_type = Column(String, default="citizen")  # citizen | officer

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    campaign = relationship("Campaign", back_populates="reports")


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)   # domain | phone | upi | sender
    value = Column(String, nullable=False)
    report_count = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    campaign = relationship("Campaign", back_populates="indicators_list")
