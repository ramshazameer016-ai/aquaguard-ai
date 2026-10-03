"""API endpoints for community report correlation."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import Report
from backend.app.schemas.correlation import CorrelationResponse
from backend.app.services.correlation_service import (
    correlate_report,
)


router = APIRouter(
    prefix="/api/correlation",
    tags=["Community Correlation"],
)


@router.get(
    "/report/{report_id}",
    response_model=CorrelationResponse,
)
def correlate_report_endpoint(
    report_id: int,
    radius_km: float = Query(
        default=1.0,
        gt=0,
        le=50,
    ),
    time_window_hours: float = Query(
        default=72.0,
        gt=0,
        le=168,
    ),
    db: Session = Depends(get_db),
) -> CorrelationResponse:
    """Find nearby and recent reports related to a target report."""

    target_report = (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )

    if target_report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    candidate_reports = (
        db.query(Report)
        .filter(Report.id != report_id)
        .all()
    )

    # Convert PostGIS geometry to latitude/longitude.
    from geoalchemy2.shape import to_shape

    target_point = to_shape(
        target_report.location
    )

    class ReportLocation:
        pass

    target_for_service = ReportLocation()

    target_for_service.id = target_report.id
    target_for_service.latitude = target_point.y
    target_for_service.longitude = target_point.x
    target_for_service.observed_at = (
        target_report.observed_at
    )

    # Report.category is stored as a string
    # in the current database model.
    target_for_service.category = str(
        target_report.category
    )

    candidate_data = []

    for report in candidate_reports:
        point = to_shape(report.location)

        candidate_for_service = ReportLocation()

        candidate_for_service.id = report.id
        candidate_for_service.latitude = point.y
        candidate_for_service.longitude = point.x
        candidate_for_service.observed_at = (
            report.observed_at
        )

        # Report.category is stored as a string.
        candidate_for_service.category = str(
            report.category
        )

        candidate_data.append(
            candidate_for_service
        )

    result = correlate_report(
        target_report=target_for_service,
        candidate_reports=candidate_data,
        radius_km=radius_km,
        time_window_hours=time_window_hours,
    )

    return CorrelationResponse(**result)