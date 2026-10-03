"""FastAPI routes for evidence-based risk outlook."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import (
    Alert,
    Event,
    EvidenceItem,
    EvidenceScore,
    RiskPrediction,
)
from backend.app.schemas.risk import (
    RiskOutlookHistoryItem,
    RiskOutlookResponse,
)
from backend.app.services.risk_service import calculate_risk_outlook


router = APIRouter(
    prefix="/api/events",
    tags=["Risk Outlook"],
)


def _calculate_event_risk_outlook(
    event_id: int,
    db: Session,
):
    """
    Calculate the current evidence-based risk outlook
    using the existing stored EvidenceScore history.
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
    # 2. Load stored Evidence Confidence history
    # ---------------------------------------------------------

    scores = (
        db.query(EvidenceScore)
        .filter(EvidenceScore.event_id == event_id)
        .order_by(
            EvidenceScore.calculated_at.asc(),
            EvidenceScore.id.asc(),
        )
        .all()
    )

    if not scores:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "No stored evidence-confidence score is "
                "available for this event. Calculate and "
                "store an evidence score before requesting "
                "the risk outlook."
            ),
        )

    current_score = float(scores[-1].score)

    previous_score = (
        float(scores[-2].score)
        if len(scores) >= 2
        else None
    )

    # ---------------------------------------------------------
    # 3. Count supporting evidence
    # ---------------------------------------------------------

    supporting_evidence_count = (
        db.query(EvidenceItem)
        .filter(
            EvidenceItem.event_id == event_id,
            EvidenceItem.direction == "supporting",
        )
        .count()
    )

    # ---------------------------------------------------------
    # 4. Count conflicting evidence
    # ---------------------------------------------------------

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
    # 6. Calculate risk outlook
    # ---------------------------------------------------------

    outlook = calculate_risk_outlook(
        event_status=event.status,
        current_evidence_confidence=current_score,
        previous_evidence_confidence=previous_score,
        supporting_evidence_count=supporting_evidence_count,
        conflicting_evidence_count=conflicting_evidence_count,
        active_alert_count=active_alert_count,
    )

    return event, current_score, previous_score, outlook


def _store_risk_prediction(
    *,
    event_id: int,
    outlook: dict,
    db: Session,
) -> RiskPrediction:
    """
    Persist the current risk-outlook snapshot.

    If the newly calculated outlook is identical to the latest
    stored snapshot, reuse the existing prediction instead of
    creating a duplicate history record.

    This prevents repeated GET requests from creating identical
    history entries while still allowing a new snapshot whenever
    the calculated risk outlook actually changes.
    """

    risk_score = float(
        outlook["risk_outlook_score"]
    )

    outlook_window = str(
        outlook["outlook_window"]
    )

    prediction_type = (
        "evidence_based_short_term"
    )

    factors_json = json.dumps(
        outlook["factors"],
        sort_keys=True,
    )

    # ---------------------------------------------------------
    # Check the latest stored snapshot
    # ---------------------------------------------------------

    latest_prediction = (
        db.query(RiskPrediction)
        .filter(
            RiskPrediction.event_id == event_id
        )
        .order_by(
            RiskPrediction.id.desc()
        )
        .first()
    )

    if latest_prediction is not None:
        latest_factors = latest_prediction.factors or "[]"

        try:
            latest_factors_json = json.dumps(
                json.loads(latest_factors),
                sort_keys=True,
            )
        except (
            TypeError,
            json.JSONDecodeError,
        ):
            latest_factors_json = latest_factors

        same_score = (
            float(latest_prediction.risk_score)
            == risk_score
        )

        same_window = (
            str(latest_prediction.outlook_window)
            == outlook_window
        )

        same_prediction_type = (
            str(latest_prediction.prediction_type)
            == prediction_type
        )

        same_factors = (
            latest_factors_json
            == factors_json
        )

        if (
            same_score
            and same_window
            and same_prediction_type
            and same_factors
        ):
            return latest_prediction

    # ---------------------------------------------------------
    # Create a genuinely new snapshot
    # ---------------------------------------------------------

    prediction = RiskPrediction(
        event_id=event_id,
        prediction_type=prediction_type,
        risk_score=risk_score,
        outlook_window=outlook_window,
        factors=factors_json,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


@router.get(
    "/{event_id}/risk-outlook",
    response_model=RiskOutlookResponse,
    status_code=status.HTTP_200_OK,
)
def get_risk_outlook(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    Calculate and persist the current short-term risk outlook.

    An identical consecutive outlook reuses the latest stored
    prediction instead of creating a duplicate history snapshot.
    """

    (
        event,
        current_score,
        previous_score,
        outlook,
    ) = _calculate_event_risk_outlook(
        event_id=event_id,
        db=db,
    )

    prediction = _store_risk_prediction(
        event_id=event.id,
        outlook=outlook,
        db=db,
    )

    return RiskOutlookResponse(
        event_id=event.id,
        event_status=event.status,
        prediction_id=prediction.id,
        **outlook,
    )


@router.get(
    "/{event_id}/risk-outlook/history",
    response_model=list[RiskOutlookHistoryItem],
    status_code=status.HTTP_200_OK,
)
def get_risk_outlook_history(
    event_id: int,
    db: Session = Depends(get_db),
):
    """
    Return persisted risk-outlook snapshots for an event.
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

    predictions = (
        db.query(RiskPrediction)
        .filter(
            RiskPrediction.event_id == event_id
        )
        .order_by(
            RiskPrediction.created_at.asc(),
            RiskPrediction.id.asc(),
        )
        .all()
    )

    history = []

    for prediction in predictions:
        try:
            factors = json.loads(
                prediction.factors or "[]"
            )
        except (
            TypeError,
            json.JSONDecodeError,
        ):
            factors = []

        history.append(
            RiskOutlookHistoryItem(
                prediction_id=prediction.id,
                event_id=prediction.event_id,
                prediction_type=prediction.prediction_type,
                risk_score=float(
                    prediction.risk_score
                ),
                outlook_window=prediction.outlook_window,
                factors=factors,
                created_at=prediction.created_at.isoformat(),
            )
        )

    return history