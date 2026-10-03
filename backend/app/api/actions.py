"""FastAPI routes for recommended event actions."""

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import (
    Alert,
    Event,
    EvidenceItem,
    EvidenceScore,
    RecommendedAction,
    RiskPrediction,
)
from backend.app.schemas.action import (
    RecommendedActionGenerationResponse,
    RecommendedActionResponse,
)
from backend.app.services.action_service import (
    generate_recommended_actions,
)


router = APIRouter(
    prefix="/api/events",
    tags=["Recommended Actions"],
)


@router.post(
    "/{event_id}/recommended-actions/generate",
    response_model=RecommendedActionGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_event_actions(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate and persist advisory actions for an event.

    Existing recommendations are not deleted or modified.
    Each generation creates a new auditable snapshot.
    """

    # ---------------------------------------------------------
    # 1. Find event
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # 2. Get latest Evidence Confidence
    # ---------------------------------------------------------

    latest_score = (
        db.query(EvidenceScore)
        .filter(EvidenceScore.event_id == event_id)
        .order_by(
            EvidenceScore.calculated_at.desc(),
            EvidenceScore.id.desc(),
        )
        .first()
    )

    if latest_score is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No stored evidence-confidence score is "
                "available for this event. Calculate the "
                "evidence score before generating actions."
            ),
        )

    evidence_confidence = float(latest_score.score)

    # ---------------------------------------------------------
    # 3. Derive current risk band from latest risk prediction
    # ---------------------------------------------------------

    latest_risk = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.event_id == event_id)
        .order_by(
            RiskPrediction.created_at.desc(),
            RiskPrediction.id.desc(),
        )
        .first()
    )

    if latest_risk is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No stored risk outlook is available for this "
                "event. Calculate the risk outlook before "
                "generating recommended actions."
            ),
        )

    risk_score = float(latest_risk.risk_score)

    if risk_score >= 70:
        risk_band = "high"
    elif risk_score >= 40:
        risk_band = "moderate"
    elif risk_score >= 20:
        risk_band = "low"
    else:
        risk_band = "minimal"

    # ---------------------------------------------------------
    # 4. Count evidence context
    # ---------------------------------------------------------

    supporting_evidence_count = (
        db.query(EvidenceItem)
        .filter(
            EvidenceItem.event_id == event_id,
            EvidenceItem.direction == "supporting",
        )
        .count()
    )

    conflicting_evidence_count = (
        db.query(EvidenceItem)
        .filter(
            EvidenceItem.event_id == event_id,
            EvidenceItem.direction == "conflicting",
        )
        .count()
    )

    # ---------------------------------------------------------
    # 5. Count active authority alerts
    # ---------------------------------------------------------

    active_alert_count = (
        db.query(Alert)
        .filter(
            Alert.event_id == event_id,
            Alert.is_active.is_(True),
        )
        .count()
    )

    # ---------------------------------------------------------
    # 6. Generate deterministic recommendations
    # ---------------------------------------------------------

    action_definitions = generate_recommended_actions(
        event_status=event.status,
        risk_band=risk_band,
        evidence_confidence=evidence_confidence,
        supporting_evidence_count=supporting_evidence_count,
        conflicting_evidence_count=conflicting_evidence_count,
        active_alert_count=active_alert_count,
    )

    # ---------------------------------------------------------
    # 7. Persist recommendations
    # ---------------------------------------------------------

    saved_actions = []

    for action in action_definitions:
        recommendation = RecommendedAction(
            event_id=event.id,
            action_type=action["action_type"],
            description=action["description"],
            priority=action["priority"],
        )

        db.add(recommendation)
        saved_actions.append(recommendation)

    db.commit()

    for recommendation in saved_actions:
        db.refresh(recommendation)

    # ---------------------------------------------------------
    # 8. Return persisted actions
    # ---------------------------------------------------------

    return RecommendedActionGenerationResponse(
        event_id=event.id,
        generated_count=len(saved_actions),
        actions=[
            RecommendedActionResponse(
                id=action.id,
                event_id=action.event_id,
                action_type=action.action_type,
                description=action.description,
                priority=action.priority,
                created_at=action.created_at,
            )
            for action in saved_actions
        ],
        human_review_required=True,
        automatic_execution=False,
    )


@router.get(
    "/{event_id}/recommended-actions",
    response_model=list[RecommendedActionResponse],
    status_code=status.HTTP_200_OK,
)
def get_event_actions(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    Return persisted recommended actions for an event.
    """

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

    actions = (
        db.query(RecommendedAction)
        .filter(RecommendedAction.event_id == event_id)
        .order_by(
            RecommendedAction.created_at.asc(),
            RecommendedAction.id.asc(),
        )
        .all()
    )

    return [
        RecommendedActionResponse(
            id=action.id,
            event_id=action.event_id,
            action_type=action.action_type,
            description=action.description,
            priority=action.priority,
            created_at=action.created_at,
        )
        for action in actions
    ]