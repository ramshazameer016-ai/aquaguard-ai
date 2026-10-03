"""SQLAlchemy ORM models defining the AquaGuard AI database schema.

AquaGuard AI architecture principles:
1. Citizen reports represent unconfirmed observations (evidence), NOT confirmed pollution.
2. Evidence Confidence belongs to potential events, not citizens.
3. Environmental data provides contextual evidence and must explicitly record simulation status.
4. Structural tables for future stages (verification, history, alerts, risk, actions) exist as schema foundations.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from backend.app.database.connection import Base


class Report(Base):
    """Citizen observation report table.

    A report represents an observation of unusual water conditions reported by
    a citizen. It is raw evidence and does NOT constitute confirmed pollution.
    """

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # PostGIS Point (longitude, latitude) with WGS84 spatial reference (SRID 4326)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)  # e.g., dead_fish, discoloration, odor, surface_sheen
    observed_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    image_path = Column(String(255), nullable=True)
    reporter_hash = Column(String(64), nullable=True)  # Anonymized reporter identifier

    # Relationship to future AI analysis of this observation
    ai_analyses = relationship("AIAnalysis", back_populates="report", cascade="all, delete-orphan")


class Event(Base):
    """Potential aquatic-health anomaly event table.

    An event represents a potential anomaly formed from multiple pieces of evidence.
    Evidence Confidence is calculated for an event, not an individual citizen.
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    # PostGIS Point (longitude, latitude) representing the epicenter/cluster center
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    status = Column(String(50), default="potential", nullable=False)  # potential, under_investigation, verified, resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships to evidence, scores, and lifecycle tables
    evidence_items = relationship("EvidenceItem", back_populates="event", cascade="all, delete-orphan")
    evidence_scores = relationship("EvidenceScore", back_populates="event", cascade="all, delete-orphan")
    verification_events = relationship("VerificationEvent", back_populates="event", cascade="all, delete-orphan")
    event_history = relationship("EventHistory", back_populates="event", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="event", cascade="all, delete-orphan")
    risk_predictions = relationship("RiskPrediction", back_populates="event", cascade="all, delete-orphan")
    recommended_actions = relationship("RecommendedAction", back_populates="event", cascade="all, delete-orphan")


class EnvironmentalObservation(Base):
    """Environmental context observation table.

    Provides environmental context (e.g. rainfall, water temperature, dissolved oxygen).
    Does NOT automatically establish pollution causation.
    The `is_simulated` field is mandatory to distinguish real vs demo/simulated data.
    """

    __tablename__ = "environmental_observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    observed_at = Column(DateTime(timezone=True), nullable=False)
    parameter = Column(String(100), nullable=False)  # rainfall, temperature, dissolved_oxygen, turbidity, pH
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # mm, C, mg/L, NTU, pH_units
    source = Column(String(100), nullable=False)  # simulated_sensor, usgs_water, weather_station
    data_quality = Column(String(50), default="provisional", nullable=False)  # provisional, verified, low
    is_simulated = Column(Boolean, default=True, nullable=False)  # Mandatory flag
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AIAnalysis(Base):
    """AI analysis result for citizen reports.

    Foundation table for future AI analysis (visual indicators, summary).
    Does not scientifically prove pollution.
    """

    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    analysis_type = Column(String(100), nullable=False)  # vision_indicator_detection, text_sentiment, etc.
    indicators = Column(JSON, nullable=True)  # List/map of detected visual/textual cues
    summary = Column(Text, nullable=True)
    model_name = Column(String(100), nullable=True)
    model_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    report = relationship("Report", back_populates="ai_analyses")


class EvidenceItem(Base):
    """Discrete evidence item contributing to Evidence Confidence.

    Direction indicates how the evidence relates to the potential anomaly:
    - supporting: evidence reinforces anomaly hypothesis
    - conflicting: evidence suggests normal seasonal/natural conditions
    - neutral: provides background context without clear valence
    """

    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String(50), nullable=False)  # photo, text, community, weather, water_quality, historical
    source_id = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    direction = Column(String(20), nullable=False)  # supporting, conflicting, neutral
    data_quality = Column(String(50), default="medium", nullable=False)  # high, medium, low
    is_simulated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="evidence_items")


class EvidenceScore(Base):
    """Calculated Evidence Confidence for an aquatic-health anomaly event.

    Score represents how strongly available evidence supports an anomaly.
    Belongs to an event, NOT to an individual citizen.
    """

    __tablename__ = "evidence_scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)  # Numerical score e.g., 0.0 to 100.0
    band = Column(String(50), nullable=False)  # low, moderate, high, critical
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    model_version = Column(String(50), nullable=True)

    event = relationship("Event", back_populates="evidence_scores")


# =========================================================================
# Structural Foundation Tables for Future Workflows (Stages 8-15)
# Business logic for these tables is NOT implemented in Stage 1.
# =========================================================================


class VerificationEvent(Base):
    """Human verification actions by designated human reviewers."""

    __tablename__ = "verification_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    verifier_id = Column(String(100), nullable=False)
    decision = Column(String(50), nullable=False)  # confirmed_anomaly, natural_phenomenon, inconclusive, false_alarm
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="verification_events")


class EventHistory(Base):
    """Append-only audit trail of state transitions for an anomaly event."""

    __tablename__ = "event_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)  # created, evidence_added, score_updated, status_changed
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    actor = Column(String(100), nullable=True)  # system, reviewer_id, etc.
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="event_history")


class Alert(Base):
    """Official alerts approved for community or authority notification."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    alert_level = Column(String(50), nullable=False)  # advisory, watch, warning, emergency
    message = Column(Text, nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    event = relationship("Event", back_populates="alerts")


class RiskPrediction(Base):
    """Short-term risk outlooks and forecasts."""

    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    prediction_type = Column(String(100), nullable=False)  # bloom_spread, hypoxia_risk, downstream_impact
    risk_score = Column(Float, nullable=False)
    outlook_window = Column(String(50), nullable=True)  # 24h, 48h, 72h
    factors = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="risk_predictions")


class RecommendedAction(Base):
    """Recommended testing, inspection, or intervention actions."""

    __tablename__ = "recommended_actions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False)  # water_sample_collection, site_inspection, public_notice
    description = Column(Text, nullable=False)
    priority = Column(String(50), default="medium", nullable=False)  # low, medium, high, urgent
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    event = relationship("Event", back_populates="recommended_actions")
