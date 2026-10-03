"""Pydantic schemas for environmental observations."""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class EnvironmentalObservationCreate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

    observed_at: datetime

    parameter: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    value: float

    unit: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    source: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    data_quality: str = Field(
        default="provisional",
        max_length=50,
    )

    is_simulated: bool = False


class EnvironmentalObservationResponse(BaseModel):
    id: int
    latitude: float
    longitude: float
    observed_at: datetime
    parameter: str
    value: float
    unit: str
    source: str
    data_quality: str
    is_simulated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnvironmentalObservationListResponse(BaseModel):
    items: List[EnvironmentalObservationResponse]
    total: int