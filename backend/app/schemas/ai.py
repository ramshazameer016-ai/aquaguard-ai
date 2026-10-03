"""Pydantic schemas for AI evidence analysis."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TextIndicator(BaseModel):
    indicator: str
    signal: float
    matches: List[str]
    negated_matches: List[str]


class TextAnalysisResponse(BaseModel):
    text_analyzed: bool
    overall_signal: float
    indicator_count: int
    indicators: List[TextIndicator]
    assessment: str
    calibration_status: str


class ReportAIAnalysisResponse(BaseModel):
    report_id: int
    category: str
    description: str
    text_analysis: Dict[str, Any]
    photo_analysis_available: bool
    photo_analysis: Optional[Dict[str, Any]] = None
    assessment: str