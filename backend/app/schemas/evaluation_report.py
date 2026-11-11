from typing import Optional, Literal
from pydantic import BaseModel, Field
# 1. Individual Requirement Assessment
class RequirementAssessment(BaseModel):

    requirement_id: int

    requirement_type: Literal[
        "Skill",
        "Education"
    ]

    requirement_value: str

    status: Literal[
        "Matched",
        "Confirmed Mismatch",
        "Evidence Not Found"
    ]

    evidence: list[str] = Field(default_factory=list)

    explanation: str


# 2. Experience Assessment

class ExperienceAssessment(BaseModel):

    requirement_id: int

    required_years: float

    estimated_years: Optional[float] = None

    status: Literal[
        "Matched",
        "Confirmed Mismatch",
        "Evidence Not Found"
    ]

    evidence: list[str] = Field(default_factory=list)

    explanation: str


# 3. Complete AI Evaluation Report

class EvaluationReport(BaseModel):

    skills: list[RequirementAssessment]

    education: list[RequirementAssessment]

    experience: list[ExperienceAssessment]

    missing_requirements: list[str]

    overall_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100
    )

    recommendation: Literal[
        "Strong Match",
        "Partial Match",
        "Weak Match"
    ]

    summary: str