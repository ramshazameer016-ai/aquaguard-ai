"""FastAPI routes for One Health contextual assessment."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import (
    EnvironmentalObservation,
    Event,
    EvidenceItem,
)
from backend.app.schemas.one_health import (
    OneHealthAssessmentResponse,
)
from backend.app.services.one_health_service import (
    assess_one_health_context,
)


router = APIRouter(
    prefix="/api/events",
    tags=["One Health"],
)


@router.get(
    "/{event_id}/one-health",
    response_model=OneHealthAssessmentResponse,
    status_code=status.HTTP_200_OK,
)
def get_one_health_assessment(
    event_id: int,
    db: Session = Depends(get_db),
):
    """Return a contextual One Health assessment for an event."""

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

    evidence_items = (
        db.query(EvidenceItem)
        .filter(
            EvidenceItem.event_id == event_id
        )
        .order_by(
            EvidenceItem.created_at.asc()
        )
        .all()
    )

    environmental_observations = (
        db.query(EnvironmentalObservation)
        .order_by(
            EnvironmentalObservation.observed_at.desc()
        )
        .limit(20)
        .all()
    )

    assessment = assess_one_health_context(
        event_status=event.status,
        event_title=event.title,
        evidence_items=evidence_items,
        environmental_observations=environmental_observations,
    )

    return OneHealthAssessmentResponse(
        event_id=event.id,
        event_status=event.status,
        **assessment,
    )