from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Email Record Create Schema
class EmailRecordCreate(BaseModel):

    email_type: str = Field(
        min_length=1,
        max_length=50
    )

    recipient_email: EmailStr


# Email Record Response Schema
class EmailRecordResponse(BaseModel):

    email_id: int

    application_id: int

    email_type: str

    recipient_email: EmailStr

    delivery_status: Literal[
        "Pending",
        "Sending",
        "Sent",
        "Failed"
    ]

    retry_count: int

    idempotency_key: str

    provider_message_id: str | None

    sent_at: datetime | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)