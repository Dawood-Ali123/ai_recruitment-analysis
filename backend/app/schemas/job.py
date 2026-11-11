
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.job_requirement import JobRequirementResponse

# Create Job Schema
class JobCreate(BaseModel):

    title: str = Field(
        min_length=3,
        max_length=150
    )

    description: str = Field(
        min_length=10
    )


# Update Job Schema
class JobUpdate(BaseModel):

    title: str | None = Field(
        default=None,
        min_length=3,
        max_length=150
    )

    description: str | None = Field(
        default=None,
        min_length=10
    )

    status: Literal[
        "Draft",
        "Open",
        "Closed",
        "Archived"
    ] | None = None


# Job Response Schema
class JobResponse(BaseModel):

    job_id: int

    title: str

    description: str

    created_by: int

    status: Literal[
        "Draft",
        "Open",
        "Closed",
        "Archived"
    ]

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobDetailsResponse(JobResponse):
    requirements:list[JobRequirementResponse]=[]