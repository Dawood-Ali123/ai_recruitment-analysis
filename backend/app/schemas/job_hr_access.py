from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Grant Job Access Schema
class JobHRAccessCreate(BaseModel):

    hr_user_id: int = Field(
        gt=0
    )


# Job HR Access Response Schema
class JobHRAccessResponse(BaseModel):

    access_id: int

    job_id: int

    hr_user_id: int

    granted_at: datetime

    model_config = ConfigDict(from_attributes=True)