from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# CV File Upload Schema
class CVFileCreate(BaseModel):

    original_filename: str = Field(
        min_length=1,
        max_length=255
    )

    mime_type: str = Field(
        max_length=100
    )

    file_size_bytes: int = Field(
        gt=0
    )


# CV File Response Schema
class CVFileResponse(BaseModel):

    cv_file_id: int

    application_id: int

    original_filename: str

    storage_key: str

    mime_type: str

    file_size_bytes: int

    version: int

    is_current: bool

    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)