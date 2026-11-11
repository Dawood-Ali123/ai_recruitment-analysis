from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Audit Log Create Schema
class AuditLogCreate(BaseModel):

    action: str = Field(
        min_length=1,
        max_length=100
    )

    entity_type: str = Field(
        min_length=1,
        max_length=50
    )

    entity_id: int | None = None

    details: dict[str, Any] | None = None


# Audit Log Response Schema
class AuditLogResponse(BaseModel):

    log_id: int

    application_id: int | None

    actor_id: int | None

    action: str

    entity_type: str

    entity_id: int | None

    details: dict[str, Any] | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)