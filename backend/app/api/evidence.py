"""FastAPI routes for event evidence."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import EvidenceItem, Event
from backend.app.schemas.evidence import (
    EvidenceCreate,
    EvidenceResponse,
    EvidenceListResponse,
)


router = APIRouter(
    prefix="/api",
    tags=["Evidence"],
)


@router.post(
    "/events/{event_id}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_evidence(
    event_id: int,
    evidence_in: EvidenceCreate,
    db: Session = Depends(get_db),
) -> EvidenceResponse:
    """Add an evidence item to an existing potential anomaly event."""

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

    evidence = EvidenceItem(
        event_id=event_id,
        evidence_type=evidence_in.evidence_type,
        source_id=evidence_in.source_id,
        description=evidence_in.description,
        direction=evidence_in.direction,
        data_quality=evidence_in.data_quality,
        is_simulated=evidence_in.is_simulated,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


@router.get(
    "/events/{event_id}/evidence",
    response_model=EvidenceListResponse,
    status_code=status.HTTP_200_OK,
)
def list_event_evidence(
    event_id: int,
    db: Session = Depends(get_db),
) -> EvidenceListResponse:
    """Return all evidence items belonging to an event."""

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
        .filter(EvidenceItem.event_id == event_id)
        .order_by(EvidenceItem.created_at.desc())
        .all()
    )

    return EvidenceListResponse(
        items=evidence_items,
        total=len(evidence_items),
    )


@router.get(
    "/evidence/{evidence_id}",
    response_model=EvidenceResponse,
    status_code=status.HTTP_200_OK,
)
def get_evidence(
    evidence_id: int,
    db: Session = Depends(get_db),
) -> EvidenceResponse:
    """Return a single evidence item."""

    evidence = (
        db.query(EvidenceItem)
        .filter(EvidenceItem.id == evidence_id)
        .first()
    )

    if evidence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence item not found.",
        )

    return evidence