from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    Text,
    DateTime,
    Identity,
    ForeignKey,
    CheckConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class HRDecision(Base):

    __tablename__ = "hr_decisions"

    __table_args__ = (
        CheckConstraint(
            "decision IN ('Shortlisted', 'Rejected', 'Request Information')",
            name="hr_decisions_decision_check"
        ),
    )

    decision_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    application_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "applications.application_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    decided_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.user_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    decision: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )