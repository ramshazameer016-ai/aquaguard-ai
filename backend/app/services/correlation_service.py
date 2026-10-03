"""Services for correlating nearby citizen reports."""

from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Any, Dict, List


# MVP correlation thresholds.
# These are engineering thresholds for grouping reports,
# not scientifically validated pollution thresholds.
DEFAULT_RADIUS_KM = 1.0
DEFAULT_TIME_WINDOW_HOURS = 72.0


def haversine_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """Calculate distance between two geographic points."""

    earth_radius_km = 6371.0

    lat1 = radians(latitude_1)
    lat2 = radians(latitude_2)

    delta_lat = radians(latitude_2 - latitude_1)
    delta_lon = radians(longitude_2 - longitude_1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * asin(sqrt(a))

    return earth_radius_km * c


def normalize_datetime(value: datetime) -> datetime:
    """Convert a datetime to timezone-aware UTC."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def hours_between(
    datetime_1: datetime,
    datetime_2: datetime,
) -> float:
    """Return absolute time difference in hours."""

    first = normalize_datetime(datetime_1)
    second = normalize_datetime(datetime_2)

    return abs(
        (first - second).total_seconds()
    ) / 3600.0


def categories_match(
    category_1: str,
    category_2: str,
) -> bool:
    """Check whether two reports have the same category."""

    return (
        category_1.strip().lower()
        == category_2.strip().lower()
    )


def reporter_group_key(report: Any) -> str:
    """
    Return the reporter grouping key.

    The architecture uses reporter_hash for duplicate collapsing.

    If reporter_hash is available, reports from the same reporter
    are treated as one independent source.

    For the current MVP, if reporter_hash is not yet present,
    the report ID is used as a fallback so existing reports remain
    individually countable rather than inventing reporter identity.
    """

    reporter_hash = getattr(
        report,
        "reporter_hash",
        None,
    )

    if reporter_hash:
        return f"reporter:{reporter_hash}"

    return f"report:{report.id}"


def correlate_report(
    target_report: Any,
    candidate_reports: List[Any],
    radius_km: float = DEFAULT_RADIUS_KM,
    time_window_hours: float = DEFAULT_TIME_WINDOW_HOURS,
) -> Dict[str, Any]:
    """
    Find reports that are spatially and temporally related.

    A report is considered related when it falls within both:

    - the configured geographic radius
    - the configured time window

    Category similarity is reported separately and is not
    required for correlation.

    Independent corroboration is calculated using reporter
    groups when reporter_hash is available.
    """

    related_reports = []
    category_matches = 0

    target_group = reporter_group_key(target_report)

    reporter_groups = set()

    for candidate in candidate_reports:

        # Never compare a report with itself.
        if candidate.id == target_report.id:
            continue

        distance_km = haversine_distance_km(
            target_report.latitude,
            target_report.longitude,
            candidate.latitude,
            candidate.longitude,
        )

        time_difference_hours = hours_between(
            target_report.observed_at,
            candidate.observed_at,
        )

        if (
            distance_km <= radius_km
            and time_difference_hours <= time_window_hours
        ):
            same_category = categories_match(
                target_report.category,
                candidate.category,
            )

            if same_category:
                category_matches += 1

            group_key = reporter_group_key(candidate)

            # A reporter group contributes at most one
            # independent corroborating source.
            is_new_reporter_group = (
                group_key not in reporter_groups
            )

            if is_new_reporter_group:
                reporter_groups.add(group_key)

            related_reports.append(
                {
                    "report_id": candidate.id,
                    "distance_km": round(
                        distance_km,
                        3,
                    ),
                    "time_difference_hours": round(
                        time_difference_hours,
                        2,
                    ),
                    "same_category": same_category,
                    "reporter_group": group_key,
                    "independent_reporter_group": (
                        is_new_reporter_group
                    ),
                }
            )

    # The target report is NOT counted as an independent
    # corroborating report.
    independent_report_count = len(
        reporter_groups
    )

    cluster_detected = (
        len(related_reports) >= 1
    )

    return {
        "target_report_id": target_report.id,
        "radius_km": radius_km,
        "time_window_hours": time_window_hours,
        "related_report_count": len(
            related_reports
        ),
        "independent_report_count": independent_report_count,
        "same_category_count": category_matches,
        "cluster_detected": cluster_detected,
        "related_reports": related_reports,
    }