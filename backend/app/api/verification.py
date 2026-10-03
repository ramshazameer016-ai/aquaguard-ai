"""FastAPI routes for human verification of AquaGuard AI events."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import (
    Event,
    EventHistory,
    EvidenceScore,
    VerificationEvent,
)
from backend.app.schemas.verification import (
    VerificationRequest,
    VerificationResponse,
)


router = APIRouter(
    prefix="/api/events",
    tags=["Verification"],
)


ACTION_STATUS_MAP = {
    "open": "under_review",
    "request_testing": "testing_requested",
    "confirm": "confirmed_anomaly",
    "reject": "rejected",
    "continue_monitoring": "under_review",
    "escalate": "escalated",
    "resolve": "resolved",
}


REQUIRED_NOTES_ACTIONS = {
    "reject",
    "escalate",
}


ALLOWED_BASIS = {
    "visual_review",
    "field_inspection",
    "lab_result",
    "community_consistency",
    "other",
}


def get_latest_evidence_score(
    db: Session,
    event_id: int,
) -> EvidenceScore | None:
    """Return the latest Evidence Confidence score for an event."""

    return (
        db.query(EvidenceScore)
        .filter(EvidenceScore.event_id == event_id)
        .order_by(EvidenceScore.calculated_at.desc())
        .first()
    )


def validate_action(
    event: Event,
    action: str,
    notes: str | None,
    verification_basis: str | None,
) -> None:
    """Validate a requested reviewer action."""

    if action not in ACTION_STATUS_MAP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid verification action. "
                "Allowed actions: "
                + ", ".join(ACTION_STATUS_MAP.keys())
            ),
        )

    if action in REQUIRED_NOTES_ACTIONS:
        if not notes or not notes.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Notes are required for the '{action}' action."
                ),
            )

    if action == "confirm":
        if not verification_basis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "verification_basis is required when "
                    "confirming an anomaly."
                ),
            )

        if verification_basis not in ALLOWED_BASIS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid verification_basis. Allowed values: "
                    + ", ".join(sorted(ALLOWED_BASIS))
                ),
            )

    current_status = event.status

    if action == "open":
        allowed_current_statuses = {
            "potential",
            "monitor",
            "caution",
            "investigation_recommended",
        }

    elif action == "request_testing":
        allowed_current_statuses = {
            "under_review",
        }

    elif action == "confirm":
        allowed_current_statuses = {
            "under_review",
            "testing_requested",
        }

    elif action == "reject":
        allowed_current_statuses = {
            "under_review",
            "testing_requested",
        }

    elif action == "continue_monitoring":
        allowed_current_statuses = {
            "under_review",
        }

    elif action == "escalate":
        allowed_current_statuses = {
            "confirmed_anomaly",
        }

    elif action == "resolve":
        allowed_current_statuses = {
            "confirmed_anomaly",
            "escalated",
            "rejected",
        }

    else:
        allowed_current_statuses = set()

    if current_status not in allowed_current_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Action '{action}' is not allowed when "
                f"the event is in status '{current_status}'."
            ),
        )


@router.post(
    "/{event_id}/verify",
    response_model=VerificationResponse,
    status_code=status.HTTP_200_OK,
)
def verify_event(
    event_id: int,
    verification: VerificationRequest,
    db: Session = Depends(get_db),
) -> VerificationResponse:
    """Apply a human reviewer action to an anomaly event."""

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

    validate_action(
        event=event,
        action=verification.action,
        notes=verification.notes,
        verification_basis=verification.verification_basis,
    )

    previous_status = event.status
    new_status = ACTION_STATUS_MAP[verification.action]

    latest_score = get_latest_evidence_score(
        db=db,
        event_id=event_id,
    )

    evidence_score_snapshot = (
        latest_score.score
        if latest_score is not None
        else None
    )

    verification_event = VerificationEvent(
        event_id=event_id,
        verifier_id=verification.verifier_id,
        decision=verification.action,
        notes=verification.notes,
    )

    db.add(verification_event)

    audit_details = {
        "verification_basis": verification.verification_basis,
        "evidence_score_snapshot": evidence_score_snapshot,
        "notes": verification.notes,
    }

    history = EventHistory(
        event_id=event_id,
        action=verification.action,
        previous_status=previous_status,
        new_status=new_status,
        actor=verification.verifier_id,
        details=json.dumps(audit_details),
    )

    db.add(history)

    event.status = new_status

    db.commit()

    db.refresh(verification_event)
    db.refresh(history)
    db.refresh(event)

    return VerificationResponse(
        event_id=event_id,
        previous_status=previous_status,
        new_status=new_status,
        action=verification.action,
        verifier_id=verification.verifier_id,
        notes=verification.notes,
        verification_basis=verification.verification_basis,
        evidence_score_snapshot=evidence_score_snapshot,
        created_at=verification_event.created_at,
    )
@router.get(
    "/{event_id}/verification-history",
    status_code=status.HTTP_200_OK,
)
def get_verification_history(
    event_id: int,
    db: Session = Depends(get_db),
):
    """Return the human verification history for an event."""

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

    verification_events = (
        db.query(VerificationEvent)
        .filter(
            VerificationEvent.event_id == event_id
        )
        .order_by(
            VerificationEvent.created_at.asc()
        )
        .all()
    )

    history = (
        db.query(EventHistory)
        .filter(
            EventHistory.event_id == event_id
        )
        .order_by(
            EventHistory.created_at.asc()
        )
        .all()
    )

    return {
        "event_id": event_id,
        "current_status": event.status,
        "verification_events": [
            {
                "id": item.id,
                "verifier_id": item.verifier_id,
                "decision": item.decision,
                "notes": item.notes,
                "created_at": item.created_at,
            }
            for item in verification_events
        ],
        "event_history": [
            {
                "id": item.id,
                "action": item.action,
                "previous_status": item.previous_status,
                "new_status": item.new_status,
                "actor": item.actor,
                "details": item.details,
                "created_at": item.created_at,
            }
            for item in history
        ],
    }