"""FastAPI routes for authority-approved alerts."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import (
    Alert,
    Event,
    EventHistory,
)
from backend.app.schemas.alert import (
    AlertCreateRequest,
    AlertResponse,
)


router = APIRouter(
    prefix="/api/events",
    tags=["Alerts"],
)


ALLOWED_ALERT_LEVELS = {
    "advisory",
    "watch",
    "warning",
    "emergency",
}


ALLOWED_EVENT_STATUSES = {
    "confirmed_anomaly",
    "escalated",
}


@router.post(
    "/{event_id}/alerts",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_authority_alert(
    event_id: int,
    request: AlertCreateRequest,
    db: Session = Depends(get_db),
):
    """Create an alert only after explicit authority approval."""

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

    if event.status not in ALLOWED_EVENT_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An authority-approved alert can only be issued "
                "for an event with status confirmed_anomaly "
                "or escalated."
            ),
        )

    alert_level = request.alert_level.strip().lower()

    if alert_level not in ALLOWED_ALERT_LEVELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid alert level. Allowed values are: "
                "advisory, watch, warning, emergency."
            ),
        )

    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert message cannot be empty.",
        )

    # Create the official alert.
    alert = Alert(
        event_id=event.id,
        alert_level=alert_level,
        message=message,
        is_active=True,
    )

    db.add(alert)
    db.flush()

    # Record the authority action in the audit trail.
    details = {
        "alert_id": alert.id,
        "alert_level": alert_level,
        "message": message,
        "notes": request.notes,
        "approval_type": "human_authority",
        "pollution_confirmation": False,
    }

    history = EventHistory(
        event_id=event.id,
        action="alert_issued",
        previous_status=event.status,
        new_status=event.status,
        actor=request.authority_id.strip(),
        details=json.dumps(details),
    )

    db.add(history)
    db.commit()
    db.refresh(alert)

    return AlertResponse(
        id=alert.id,
        event_id=alert.event_id,
        alert_level=alert.alert_level,
        message=alert.message,
        issued_by=request.authority_id.strip(),
        issued_at=alert.issued_at,
        is_active=alert.is_active,
        notes=request.notes,
    )