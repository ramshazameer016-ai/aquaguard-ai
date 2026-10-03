"""FastAPI routes for Potential Aquatic-Health Anomaly Events."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from backend.app.database.connection import get_db
from backend.app.database.models import Event
from backend.app.schemas.event import (
    EventCreate,
    EventResponse,
    EventListResponse,
)
from backend.app.services.report_service import extract_point_coordinates


router = APIRouter(
    prefix="/api/events",
    tags=["Events"],
)


def event_to_response(event: Event) -> EventResponse:
    """Convert an Event ORM object into the API response schema."""

    longitude, latitude = extract_point_coordinates(event.location)

    return EventResponse(
        id=event.id,
        title=event.title,
        status=event.status,
        latitude=latitude,
        longitude=longitude,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
) -> EventResponse:
    """Create a potential aquatic-health anomaly event."""

    location_geom = WKTElement(
        f"POINT({event_in.longitude} {event_in.latitude})",
        srid=4326,
    )

    event = Event(
        title=event_in.title,
        location=location_geom,
        status=event_in.status,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event_to_response(event)


@router.get(
    "",
    response_model=EventListResponse,
    status_code=status.HTTP_200_OK,
)
def list_events(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> EventListResponse:
    """Return paginated potential aquatic-health anomaly events."""

    skip = (page - 1) * limit

    total = db.query(Event).count()

    events = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return EventListResponse(
        items=[event_to_response(event) for event in events],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
) -> EventResponse:
    """Return a single potential aquatic-health anomaly event."""

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found.",
        )

    return event_to_response(event)