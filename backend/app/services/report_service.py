"""Service layer for Citizen Report operations."""

import struct

from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from geoalchemy2.elements import WKTElement

from backend.app.database.models import Report, Event
from backend.app.schemas.report import ReportCreate, ReportResponse


def extract_point_coordinates(
    geom,
) -> Tuple[float, float]:
    """Extract (longitude, latitude) from a PostGIS geometry or WKBElement.

    Handles EWKB binary elements from PostGIS where coordinates are stored
    as IEEE 754 64-bit floats (little-endian or big-endian).
    """

    if geom is None:
        return 0.0, 0.0

    # Binary WKB / EWKB
    if hasattr(geom, "data"):
        raw = bytes(geom.data)

        if len(raw) >= 16:
            endian = "<" if raw[0] == 1 else ">"

            x, y = struct.unpack(
                f"{endian}dd",
                raw[-16:],
            )

            return float(x), float(y)

    # String / WKT fallback
    s = str(geom).upper()

    if "POINT" in s:
        try:
            coords_str = (
                s[s.index("(") + 1 : s.index(")")]
                .strip()
            )

            parts = coords_str.split()

            if len(parts) >= 2:
                return float(parts[0]), float(parts[1])

        except Exception:
            pass

    return 0.0, 0.0


def report_to_response(
    report: Report,
) -> ReportResponse:
    """Transform an ORM Report model into an API ReportResponse schema."""

    lon, lat = extract_point_coordinates(
        report.location
    )

    return ReportResponse(
        id=report.id,
        category=report.category,
        description=report.description,
        latitude=lat,
        longitude=lon,
        observed_at=report.observed_at,
        created_at=report.created_at,
        image_path=report.image_path,
    )


class ReportService:
    """Encapsulates report creation, retrieval, and listing logic."""

    @staticmethod
    def create_report(
        db: Session,
        report_in: ReportCreate,
    ) -> Tuple[Report, Event]:
        """Store a citizen observation and create its potential event.

        A citizen report is an observation/evidence item. It does not
        constitute confirmed pollution. A corresponding Event is created
        with status='potential' so the authority dashboard can track the
        observation through the existing event workflow.

        Returns:
            A tuple containing the created Report and its corresponding
            Event.
        """

        observed_at = (
            report_in.observed_at
            or datetime.now(timezone.utc)
        )

        location_geom = WKTElement(
            f"POINT({report_in.longitude} {report_in.latitude})",
            srid=4326,
        )

        # ---------------------------------------------------------
        # 1. Create the citizen report
        # ---------------------------------------------------------

        db_report = Report(
            location=location_geom,
            description=report_in.description,
            category=report_in.category,
            observed_at=observed_at,
            image_path=report_in.image_path,
        )

        db.add(db_report)

        # Flush so the Report receives its database ID before
        # the transaction is committed.
        db.flush()

        # ---------------------------------------------------------
        # 2. Create the corresponding potential anomaly event
        # ---------------------------------------------------------

        category_label = (
            report_in.category.replace("_", " ").strip()
            if report_in.category
            else "water condition"
        )

        event = Event(
            title=f"Potential {category_label} observation",
            location=location_geom,
            status="potential",
        )

        db.add(event)

        # Flush so the Event receives its database ID before
        # returning it to the caller.
        db.flush()

        # ---------------------------------------------------------
        # 3. Commit Report + Event together
        # ---------------------------------------------------------

        db.commit()

        # Refresh both objects so the caller receives their final
        # database-generated fields.
        db.refresh(db_report)
        db.refresh(event)

        return db_report, event

    @staticmethod
    def get_report_by_id(
        db: Session,
        report_id: int,
    ) -> Optional[Report]:
        """Retrieve a citizen report by primary key ID."""

        return (
            db.query(Report)
            .filter(Report.id == report_id)
            .first()
        )

    @staticmethod
    def list_reports(
        db: Session,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Report], int]:
        """List citizen reports with pagination, ordered by creation date descending."""

        total = db.query(Report).count()

        reports = (
            db.query(Report)
            .order_by(
                Report.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return reports, total