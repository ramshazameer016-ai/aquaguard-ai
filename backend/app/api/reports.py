"""FastAPI routes for citizen observation reports."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy.orm import Session

from backend.app.database.connection import get_db

from backend.app.schemas.report import (
    ReportCreate,
    ReportCreateResponse,
    ReportListResponse,
    ReportResponse,
)

from backend.app.services.report_service import (
    ReportService,
    report_to_response,
)


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
)


@router.post(
    "",
    response_model=ReportCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
) -> ReportCreateResponse:
    """Create a new citizen observation report and its potential event."""

    report, event = ReportService.create_report(
        db,
        report_in,
    )

    return ReportCreateResponse(
        id=report.id,
        event_id=event.id,
        status="received",
        message="Observation received successfully.",
    )


@router.get(
    "",
    response_model=ReportListResponse,
    status_code=status.HTTP_200_OK,
)
def list_reports(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ReportListResponse:
    """Return paginated citizen observation reports."""

    skip = (page - 1) * limit

    reports, total = ReportService.list_reports(
        db,
        skip=skip,
        limit=limit,
    )

    return ReportListResponse(
        items=[
            report_to_response(report)
            for report in reports
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    status_code=status.HTTP_200_OK,
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
) -> ReportResponse:
    """Return a single citizen observation report."""

    report = ReportService.get_report_by_id(
        db,
        report_id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found.",
        )

    return report_to_response(report)