"""Pydantic schemas for community correlation."""

from typing import List

from pydantic import BaseModel, Field


class RelatedReport(BaseModel):
    report_id: int
    distance_km: float
    time_difference_hours: float
    same_category: bool


class CorrelationResponse(BaseModel):
    target_report_id: int
    radius_km: float
    time_window_hours: float
    related_report_count: int
    independent_report_count: int
    same_category_count: int
    cluster_detected: bool
    related_reports: List[RelatedReport]