from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# Create Job Requirement Schema
class JobRequirementCreate(BaseModel):

    requirement_type: Literal[
        "Skill",
        "Education",
        "Experience"
    ]

    requirement_value: str = Field(
        min_length=1,
        max_length=255
    )

    is_mandatory: bool = True

    minimum_years: Decimal | None = Field(
        default=None,
        ge=0
    )

    @model_validator(mode="after")
    def validate_minimum_years(self):

        if (
            self.requirement_type != "Experience"
            and self.minimum_years is not None
        ):
            raise ValueError(
                "minimum_years is only allowed for Experience requirements"
            )

        return self


# Job Requirement Response Schema
class JobRequirementResponse(BaseModel):

    requirement_id: int

    job_id: int

    requirement_type: Literal[
        "Skill",
        "Education",
        "Experience"
    ]

    requirement_value: str

    is_mandatory: bool

    minimum_years: Decimal | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)