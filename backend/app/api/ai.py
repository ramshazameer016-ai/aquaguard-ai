"""API endpoints for AI evidence analysis."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.ai.text_analysis import analyze_text
from backend.app.ai.vision_analysis import analyze_image
from backend.app.database.connection import get_db
from backend.app.database.models import (
    Report,
    Event,
    EvidenceScore,
)
from backend.app.services.correlation_service import correlate_report
from backend.app.services.fusion_service import fuse_evidence
from backend.app.schemas.ai import ReportAIAnalysisResponse


router = APIRouter(
    prefix="/api/ai",
    tags=["AI Evidence Analysis"],
)


def _build_report_location(report):
    """Convert a database Report location into the format
    expected by the correlation service.
    """
    from geoalchemy2.shape import to_shape

    point = to_shape(report.location)

    class ReportLocation:
        pass

    result = ReportLocation()

    result.id = report.id
    result.latitude = point.y
    result.longitude = point.x
    result.observed_at = report.observed_at
    result.category = str(report.category)

    result.reporter_hash = getattr(
        report,
        "reporter_hash",
        None,
    )

    return result


def _get_community_result(
    report_id: int,
    db: Session,
):
    """Run community correlation using the same 1 km / 72 hour
    settings used by the Stage 5 correlation API.
    """
    target_report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if target_report is None:
        return None

    candidate_reports = (
        db.query(Report)
        .filter(Report.id != report_id)
        .all()
    )

    target_for_service = _build_report_location(
        target_report
    )

    candidate_data = []

    for report in candidate_reports:
        candidate_data.append(
            _build_report_location(report)
        )

    return correlate_report(
        target_report=target_for_service,
        candidate_reports=candidate_data,
        radius_km=1.0,
        time_window_hours=72.0,
    )


def _store_evidence_score(
    *,
    event_id: int,
    fusion_result: dict,
    db: Session,
):
    """Persist the Evidence Confidence produced by the
    existing fusion engine.

    The event is supplied explicitly by the caller.

    No report_id == event_id assumption is made.

    No new scoring formula is introduced.

    If an identical latest score already exists for the same
    event and fusion version, that existing score is reused
    instead of creating a duplicate snapshot.
    """

    event = (
        db.query(Event)
        .filter(Event.id == event_id)
        .first()
    )

    if event is None:
        return None

    score_value = float(
        fusion_result["evidence_confidence"]
    )

    band_value = str(
        fusion_result["confidence_band"]
    )

    model_version = str(
        fusion_result["fusion_version"]
    )

    # Check the latest stored EvidenceScore for this event.
    latest_score = (
        db.query(EvidenceScore)
        .filter(
            EvidenceScore.event_id == event.id
        )
        .order_by(
            EvidenceScore.id.desc()
        )
        .first()
    )

    # Reuse the latest identical score rather than
    # creating duplicate rows when the same explanation
    # is requested repeatedly.
    if (
        latest_score is not None
        and float(latest_score.score) == score_value
        and str(latest_score.band) == band_value
        and str(latest_score.model_version) == model_version
    ):
        return latest_score

    evidence_score = EvidenceScore(
        event_id=event.id,
        score=score_value,
        band=band_value,
        model_version=model_version,
    )

    db.add(evidence_score)
    db.commit()
    db.refresh(evidence_score)

    return evidence_score


@router.get(
    "/report/{report_id}",
    response_model=ReportAIAnalysisResponse,
)
def analyze_report(
    report_id: int,
    db: Session = Depends(get_db),
) -> ReportAIAnalysisResponse:
    """Analyze text and optional photo evidence from a citizen report."""

    report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    description = report.description or ""

    # ---------------------------------------------------------
    # Text analysis
    # ---------------------------------------------------------

    text_result = analyze_text(description)

    # ---------------------------------------------------------
    # Photo analysis
    # ---------------------------------------------------------

    photo_result = None
    photo_available = False

    if report.image_path:
        photo_available = True

        try:
            photo_result = analyze_image(
                report.image_path
            )

        except Exception as exc:
            photo_result = {
                "vision_analyzed": False,
                "assessment": (
                    "Vision analysis unavailable. "
                    "Photo evidence is missing from the AI assessment."
                ),
                "calibration_status": "uncalibrated",
                "fallback": True,
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # Combined cautious assessment
    # ---------------------------------------------------------

    if (
        text_result["indicator_count"] > 0
        and photo_available
    ):
        assessment = (
            "Possible aquatic anomaly indicators were detected "
            "across report text and available photo evidence. "
            "These are evidence signals and do not confirm pollution."
        )

    elif text_result["indicator_count"] > 0:
        assessment = (
            "Possible aquatic anomaly indicators were detected "
            "in the report text. Photo evidence was not available "
            "for the assessment."
        )

    elif (
        photo_result
        and photo_result.get("vision_analyzed")
    ):
        assessment = (
            "Possible visual aquatic anomaly indicators were detected "
            "in the available photo. These are uncalibrated evidence "
            "signals and do not confirm pollution."
        )

    else:
        assessment = (
            "No predefined aquatic anomaly indicators were detected "
            "from the available evidence."
        )

    return ReportAIAnalysisResponse(
        report_id=report.id,
        category=str(report.category),
        description=description,
        text_analysis=text_result,
        photo_analysis_available=photo_available,
        photo_analysis=photo_result,
        assessment=assessment,
    )


@router.get(
    "/fusion/report/{report_id}",
)
def analyze_report_fusion(
    report_id: int,
    event_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Run explainable evidence fusion for one citizen report.

    The optional event_id explicitly identifies the event for which
    the resulting Evidence Confidence should be stored.

    Existing fusion mathematics are unchanged.
    """

    report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    # If an event_id is supplied, verify that it exists
    # before running and storing the fusion result.
    if event_id is not None:
        event = (
            db.query(Event)
            .filter(Event.id == event_id)
            .first()
        )

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Event not found.",
            )

    description = report.description or ""

    # ---------------------------------------------------------
    # 1. TEXT
    # ---------------------------------------------------------

    text_result = analyze_text(description)

    # ---------------------------------------------------------
    # 2. PHOTO
    # ---------------------------------------------------------

    photo_result = None

    if report.image_path:
        try:
            photo_result = analyze_image(
                report.image_path
            )

        except Exception as exc:
            photo_result = {
                "vision_analyzed": False,
                "fallback": True,
                "calibration_status": "uncalibrated",
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # 3. COMMUNITY CORRELATION
    # ---------------------------------------------------------

    community_result = _get_community_result(
        report_id=report_id,
        db=db,
    )

    # ---------------------------------------------------------
    # 4. ENVIRONMENTAL EVIDENCE
    # ---------------------------------------------------------

    # Environmental severity is not automatically inferred
    # from existing environmental records.
    environmental_result = None

    # ---------------------------------------------------------
    # 5. HISTORICAL SIMILARITY
    # ---------------------------------------------------------

    # No reviewed historical similarity module exists yet.
    historical_result = None

    # ---------------------------------------------------------
    # 6. EXISTING FUSION ENGINE
    # ---------------------------------------------------------

    fusion_result = fuse_evidence(
        text_result=text_result,
        photo_result=photo_result,
        community_result=community_result,
        environmental_result=environmental_result,
        historical_result=historical_result,
    )

    # ---------------------------------------------------------
    # 7. OPTIONAL EVIDENCE-SCORE PERSISTENCE
    # ---------------------------------------------------------

    stored_score = None

    if event_id is not None:
        stored_score = _store_evidence_score(
            event_id=event_id,
            fusion_result=fusion_result,
            db=db,
        )

    return {
        "report_id": report.id,
        "event_id": event_id,
        "category": str(report.category),
        "description": description,
        "source_analysis": {
            "text": text_result,
            "photo": photo_result,
            "community": community_result,
        },
        "fusion": fusion_result,
        "stored_evidence_score": (
            {
                "id": stored_score.id,
                "event_id": stored_score.event_id,
                "score": stored_score.score,
                "band": stored_score.band,
                "model_version": stored_score.model_version,
            }
            if stored_score is not None
            else None
        ),
    }


@router.get(
    "/explanation/report/{report_id}",
)
def get_report_explanation(
    report_id: int,
    event_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Return the explainable evidence assessment for one report.

    When event_id is supplied, the exact Evidence Confidence
    calculated for the explanation is also persisted against
    that event.

    This keeps the displayed AI assessment and the stored
    Event evidence score synchronized.
    """

    report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    # ---------------------------------------------------------
    # Verify the explicitly supplied event
    # ---------------------------------------------------------

    if event_id is not None:
        event = (
            db.query(Event)
            .filter(Event.id == event_id)
            .first()
        )

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Event not found.",
            )

    description = report.description or ""

    # ---------------------------------------------------------
    # 1. TEXT
    # ---------------------------------------------------------

    text_result = analyze_text(description)

    # ---------------------------------------------------------
    # 2. PHOTO
    # ---------------------------------------------------------

    photo_result = None

    if report.image_path:
        try:
            photo_result = analyze_image(
                report.image_path
            )

        except Exception as exc:
            photo_result = {
                "vision_analyzed": False,
                "fallback": True,
                "calibration_status": "uncalibrated",
                "error": str(exc),
            }

    # ---------------------------------------------------------
    # 3. COMMUNITY CORRELATION
    # ---------------------------------------------------------

    community_result = _get_community_result(
        report_id=report_id,
        db=db,
    )

    # ---------------------------------------------------------
    # 4. ENVIRONMENTAL EVIDENCE
    # ---------------------------------------------------------

    environmental_result = None

    # ---------------------------------------------------------
    # 5. HISTORICAL SIMILARITY
    # ---------------------------------------------------------

    historical_result = None

    # ---------------------------------------------------------
    # 6. EXISTING FUSION ENGINE
    # ---------------------------------------------------------

    fusion_result = fuse_evidence(
        text_result=text_result,
        photo_result=photo_result,
        community_result=community_result,
        environmental_result=environmental_result,
        historical_result=historical_result,
    )

    # ---------------------------------------------------------
    # 7. PERSIST EXACT FUSION SCORE WHEN EVENT IS KNOWN
    # ---------------------------------------------------------

    stored_score = None

    if event_id is not None:
        stored_score = _store_evidence_score(
            event_id=event_id,
            fusion_result=fusion_result,
            db=db,
        )

    return {
        "report_id": report.id,
        "event_id": event_id,
        "category": str(report.category),

        "assessment": {
            "evidence_confidence": fusion_result[
                "evidence_confidence"
            ],
            "confidence_band": fusion_result[
                "confidence_band"
            ],
            "ai_belief": fusion_result[
                "ai_belief"
            ],
            "belief_band": fusion_result[
                "belief_band"
            ],
            "calibration_status": fusion_result[
                "calibration_status"
            ],
            "human_verification_required": fusion_result[
                "human_verification_required"
            ],
            "is_pollution_confirmation": fusion_result[
                "is_pollution_confirmation"
            ],
        },

        "why": {
            "reasoning": fusion_result[
                "reasoning"
            ],
            "belief_factors": fusion_result[
                "belief_factors"
            ],
        },

        "supporting_evidence": fusion_result[
            "supporting_evidence"
        ],

        "conflicting_evidence": fusion_result[
            "conflicting_evidence"
        ],

        "missing_evidence": fusion_result[
            "missing_evidence"
        ],

        "contributions": fusion_result[
            "contributions"
        ],

        "stored_evidence_score": (
            {
                "id": stored_score.id,
                "event_id": stored_score.event_id,
                "score": stored_score.score,
                "band": stored_score.band,
                "model_version": stored_score.model_version,
            }
            if stored_score is not None
            else None
        ),
    }