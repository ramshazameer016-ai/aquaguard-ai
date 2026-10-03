"""Pydantic schemas for One Health contextual assessment."""

from typing import List

from pydantic import BaseModel


class OneHealthAssessmentResponse(BaseModel):
    event_id: int
    event_status: str

    environmental_context: List[str]
    ecological_context: List[str]
    human_health_context: List[str]

    attention_level: str

    supporting_context: List[str]
    limitations: List[str]

    human_verification_required: bool
    pollution_confirmation: bool
    medical_diagnosis: bool