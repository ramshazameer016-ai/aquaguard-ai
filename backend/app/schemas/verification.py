"""Pydantic schemas for human verification workflow."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VerificationRequest(BaseModel):
    """Request for a human reviewer action on an event."""

    verifier_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    action: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=5000,
    )

    verification_basis: Optional[str] = Field(
        default=None,
        max_length=255,
    )


class VerificationResponse(BaseModel):
    """Response after a human verification action."""

    event_id: int
    previous_status: str
    new_status: str
    action: str
    verifier_id: str
    notes: Optional[str] = None
    verification_basis: Optional[str] = None
    evidence_score_snapshot: Optional[float] = None
    created_at: datetime