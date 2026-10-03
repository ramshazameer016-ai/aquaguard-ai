"""FastAPI routes for the AquaGuard AI Authority Dashboard."""

from collections import Counter
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import Event
from backend.app.api.events import event_to_response


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    status_code=status.HTTP_200_OK,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
):
    """Return an authority-facing summary based on stored events."""

    events = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .all()
    )

    status_counts = Counter(
        str(event.status)
        for event in events
    )

    recent_events = [
        event_to_response(event).model_dump()
        for event in events[:10]
    ]

    return {
        "total_events": len(events),
        "status_counts": dict(status_counts),
        "recent_events": recent_events,
        "data_scope": {
            "source": "stored AquaGuard AI events",
            "generated_at": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "notes": [
            "Dashboard counts are derived from stored anomaly events.",
            "No pollution confirmation is inferred from event status.",
            "Confidence bands are not included because the current Event model does not store them.",
        ],
    }