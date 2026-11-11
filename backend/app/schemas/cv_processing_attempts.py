from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# CV Processing Attempt Create Schema
class CVProcessingAttemptCreate(BaseModel):

    evaluation_id: int = Field(
        gt=0
    )

    attempt_number: int = Field(
        ge=1,
        le=3
    )


# CV Processing Attempt Response Schema
class CVProcessingAttemptResponse(BaseModel):

    attempt_id: int

    evaluation_id: int

    attempt_number: int

    status: Literal[
        "Processing",
        "Completed",
        "Failed"
    ]

    error_code: str | None

    error_message: str | None

    started_at: datetime

    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)