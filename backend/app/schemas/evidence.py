"""Pydantic schemas for event evidence."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EvidenceCreate(BaseModel):
    """Request schema for adding evidence to a potential anomaly event."""

    evidence_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    source_id: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    description: str = Field(
        ...,
        min_length=1,
    )

    direction: str = Field(
        default="neutral",
        max_length=20,
    )

    data_quality: str = Field(
        default="medium",
        max_length=50,
    )

    is_simulated: bool = False


class EvidenceResponse(BaseModel):
    """Response schema for a single evidence item."""

    id: int
    event_id: int
    evidence_type: str
    source_id: Optional[str] = None
    description: str
    direction: str
    data_quality: str
    is_simulated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvidenceListResponse(BaseModel):
    """List of evidence items belonging to an event."""

    items: List[EvidenceResponse]
    total: int