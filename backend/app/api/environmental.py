"""API endpoints for environmental observations and weather context."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2.shape import to_shape
from geoalchemy2 import WKTElement
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import EnvironmentalObservation
from backend.app.schemas.environmental import (
    EnvironmentalObservationCreate,
    EnvironmentalObservationListResponse,
    EnvironmentalObservationResponse,
)
from backend.app.services.environmental_service import (
    fetch_open_meteo_weather,
)


router = APIRouter(
    prefix="/api/environmental",
    tags=["Environmental Data"],
)


def observation_to_response(
    observation: EnvironmentalObservation,
) -> EnvironmentalObservationResponse:
    """Convert database environmental observation to API response."""

    point = to_shape(observation.location)

    return EnvironmentalObservationResponse(
        id=observation.id,
        latitude=point.y,
        longitude=point.x,
        observed_at=observation.observed_at,
        parameter=observation.parameter,
        value=observation.value,
        unit=observation.unit,
        source=observation.source,
        data_quality=observation.data_quality,
        is_simulated=observation.is_simulated,
        created_at=observation.created_at,
    )


@router.post(
    "",
    response_model=EnvironmentalObservationResponse,
)
def create_environmental_observation(
    payload: EnvironmentalObservationCreate,
    db: Session = Depends(get_db),
) -> EnvironmentalObservationResponse:
    """Create an environmental observation."""

    observation = EnvironmentalObservation(
        location=WKTElement(
            f"POINT({payload.longitude} {payload.latitude})",
            srid=4326,
        ),
        observed_at=payload.observed_at,
        parameter=payload.parameter,
        value=payload.value,
        unit=payload.unit,
        source=payload.source,
        data_quality=payload.data_quality,
        is_simulated=payload.is_simulated,
    )

    db.add(observation)
    db.commit()
    db.refresh(observation)

    return observation_to_response(observation)


@router.get(
    "",
    response_model=EnvironmentalObservationListResponse,
)
def list_environmental_observations(
    parameter: Optional[str] = Query(
        default=None,
        description="Filter by environmental parameter.",
    ),
    source: Optional[str] = Query(
        default=None,
        description="Filter by data source.",
    ),
    is_simulated: Optional[bool] = Query(
        default=None,
        description="Filter simulated or real observations.",
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> EnvironmentalObservationListResponse:
    """List environmental observations."""

    query = db.query(EnvironmentalObservation)

    if parameter:
        query = query.filter(
            EnvironmentalObservation.parameter == parameter
        )

    if source:
        query = query.filter(
            EnvironmentalObservation.source == source
        )

    if is_simulated is not None:
        query = query.filter(
            EnvironmentalObservation.is_simulated
            == is_simulated
        )

    total = query.with_entities(
        func.count(EnvironmentalObservation.id)
    ).scalar() or 0

    observations = (
        query.order_by(
            EnvironmentalObservation.observed_at.desc()
        )
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return EnvironmentalObservationListResponse(
        items=[
            observation_to_response(observation)
            for observation in observations
        ],
        total=total,
    )


@router.get(
    "/weather",
)
def get_real_weather(
    latitude: float,
    longitude: float,
) -> dict:
    """Get real weather context from Open-Meteo."""

    if not -90 <= latitude <= 90:
        raise HTTPException(
            status_code=400,
            detail="Latitude must be between -90 and 90.",
        )

    if not -180 <= longitude <= 180:
        raise HTTPException(
            status_code=400,
            detail="Longitude must be between -180 and 180.",
        )

    try:
        return fetch_open_meteo_weather(
            latitude=latitude,
            longitude=longitude,
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get(
    "/{observation_id}",
    response_model=EnvironmentalObservationResponse,
)
def get_environmental_observation(
    observation_id: int,
    db: Session = Depends(get_db),
) -> EnvironmentalObservationResponse:
    """Get one environmental observation by ID."""

    observation = (
        db.query(EnvironmentalObservation)
        .filter(
            EnvironmentalObservation.id
            == observation_id
        )
        .first()
    )

    if observation is None:
        raise HTTPException(
            status_code=404,
            detail="Environmental observation not found.",
        )

    return observation_to_response(observation)