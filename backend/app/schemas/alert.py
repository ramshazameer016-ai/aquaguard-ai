"""Pydantic schemas for authority-approved alerts."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AlertCreateRequest(BaseModel):
    authority_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    alert_level: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=5000,
    )


class AlertResponse(BaseModel):
    id: int
    event_id: int
    alert_level: str
    message: str
    issued_by: str
    issued_at: datetime
    is_active: bool
    notes: Optional[str] = None