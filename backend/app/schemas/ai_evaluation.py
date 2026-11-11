from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


# AI Evaluation Result Schema
class AIEvaluationResult(BaseModel):

    score: Decimal = Field(
        ge=0,
        le=100
    )

    recommendation: Literal[
        "Strong Match",
        "Partial Match",
        "Not Recommended"
    ]

    skills_matching: list[str]

    experience_matching: str

    missing_requirements: list[str]

    evidence: list[str]

    explanation: str


# AI Evaluation Response Schema
class AIEvaluationResponse(BaseModel):

    evaluation_id: int

    application_id: int

    cv_file_id: int

    processing_status: Literal[
        "Pending",
        "Processing",
        "Completed",
        "Failed"
    ]

    score: Decimal | None

    report: dict[str, Any] | None

    model_name: str | None

    prompt_version: str | None

    created_at: datetime

    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)