"""Pydantic schemas for evidence-based risk outlook."""

from typing import List, Optional

from pydantic import BaseModel


class RiskOutlookResponse(BaseModel):
    event_id: int
    event_status: str

    prediction_id: Optional[int] = None

    current_evidence_confidence: float
    previous_evidence_confidence: Optional[float] = None
    evidence_momentum: float

    risk_outlook_score: float
    risk_band: str

    outlook_direction: str
    outlook_window: str

    calculation: str
    factors: List[str]
    limitations: List[str]

    human_verification_required: bool
    pollution_confirmation: bool


class RiskOutlookHistoryItem(BaseModel):
    prediction_id: int
    event_id: int
    prediction_type: str
    risk_score: float
    outlook_window: Optional[str] = None
    factors: List[str]
    created_at: str