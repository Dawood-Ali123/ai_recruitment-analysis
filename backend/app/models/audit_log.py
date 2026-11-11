from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Identity,
    ForeignKey,
    text
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    log_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    application_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "applications.application_id",
            ondelete="RESTRICT"
        ),
        nullable=True
    )

    actor_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.user_id",
            ondelete="RESTRICT"
        ),
        nullable=True
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    entity_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )

    details: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )