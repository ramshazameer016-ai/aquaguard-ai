"""Pydantic schemas for Potential Aquatic-Health Anomaly Events."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """Request schema for creating a potential aquatic-health anomaly event."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
    )

    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
    )

    status: str = Field(
        default="potential",
        max_length=50,
    )


class EventResponse(BaseModel):
    """Basic response schema for a potential aquatic-health anomaly event."""

    id: int
    title: str
    status: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    """Paginated list of potential anomaly events."""

    items: List[EventResponse]
    total: int
    page: int
    limit: int