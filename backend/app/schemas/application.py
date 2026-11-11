from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Candidate Application Schema
class ApplicationCreate(BaseModel):

    job_id: int = Field(
        gt=0
    )


# Application Status Update Schema
class ApplicationStatusUpdate(BaseModel):

    status: Literal[
        "Submitted",
        "Processing",
        "Needs Review",
        "HR Review",
        "Shortlisted",
        "Rejected",
        "Withdrawn"
    ]


# Application Response Schema
class ApplicationResponse(BaseModel):

    application_id: int

    candidate_id: int

    job_id: int

    status: Literal[
        "Submitted",
        "Processing",
        "Needs Review",
        "HR Review",
        "Shortlisted",
        "Rejected",
        "Withdrawn"
    ]

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# HR Application Response Schema
class HRApplicationResponse(ApplicationResponse):

    candidate_name: str

    candidate_email: str