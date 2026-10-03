"""Pydantic schemas for Citizen Report operations."""

from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, field_validator


class ReportCategory(str, Enum):
    """Controlled set of observation categories (extensible)."""

    FISH_MORTALITY = "fish_mortality"

    WATER_DISCOLORATION = "water_discoloration"

    FOAM_SURFACE_MATERIAL = "foam_surface_material"

    UNUSUAL_ODOR = "unusual_odor"

    WILDLIFE_ACTIVITY = "wildlife_activity"

    OTHER = "other"


class ReportCreate(BaseModel):
    """Request schema for submitting a citizen water observation."""

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude in decimal degrees between -90 and 90",
        examples=[17.385044],
    )

    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude in decimal degrees between -180 and 180",
        examples=[78.486671],
    )

    description: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Detailed description of the citizen observation",
        examples=[
            "I saw three dead fish and unusual green surface material near the embankment."
        ],
    )

    category: Optional[str] = Field(
        default=ReportCategory.OTHER.value,
        max_length=100,
        description=(
            "Category of observation "
            "(e.g. fish_mortality, water_discoloration, "
            "unusual_odor, other)"
        ),
        examples=["fish_mortality"],
    )

    observed_at: Optional[datetime] = Field(
        default=None,
        description=(
            "ISO 8601 timestamp when the observation occurred. "
            "Defaults to current server time if omitted."
        ),
        examples=["2026-10-02T10:30:00Z"],
    )

    image_path: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional relative file path or reference to photo evidence",
    )

    @field_validator("description")
    @classmethod
    def validate_description_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "Description must not be empty or whitespace only."
            )

        return v.strip()


class ReportCreateResponse(BaseModel):
    """Response returned upon successful creation of a report."""

    id: int

    # Event created from this observation so downstream
    # evidence scoring and risk assessment can target
    # the correct event.
    event_id: int

    status: str = "received"

    message: str = "Observation received successfully."


class ReportResponse(BaseModel):
    """Detailed response schema for a citizen observation report."""

    id: int

    category: Optional[str] = None

    description: str

    latitude: float

    longitude: float

    observed_at: datetime

    created_at: datetime

    image_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    """Paginated list of citizen observation reports."""

    items: List[ReportResponse]

    total: int

    page: int

    limit: int