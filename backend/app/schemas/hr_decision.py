from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# HR Decision Create Schema
class HRDecisionCreate(BaseModel):

    decision: Literal[
        "Shortlisted",
        "Rejected",
        "Request Information"
    ]

    notes: str | None = Field(
        default=None,
        max_length=2000
    )


# HR Decision Response Schema
class HRDecisionResponse(BaseModel):

    decision_id: int

    application_id: int

    decided_by: int

    decision: Literal[
        "Shortlisted",
        "Rejected",
        "Request Information"
    ]

    notes: str | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)