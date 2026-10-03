"""Pydantic schemas for recommended actions."""

from datetime import datetime
from typing import List

from pydantic import BaseModel


class RecommendedActionResponse(BaseModel):
    id: int
    event_id: int
    action_type: str
    description: str
    priority: str
    created_at: datetime


class RecommendedActionGenerationResponse(BaseModel):
    event_id: int
    generated_count: int
    actions: List[RecommendedActionResponse]
    human_review_required: bool
    automatic_execution: bool