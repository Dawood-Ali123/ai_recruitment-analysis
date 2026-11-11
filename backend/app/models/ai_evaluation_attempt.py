from datetime import datetime
from sqlalchemy import (
    Integer, String, Text, DateTime,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base


class AIEvaluationAttempt(Base):
    __tablename__ = "ai_evaluation_attempts"

    __table_args__ = (
        UniqueConstraint(
            "evaluation_id",
            "attempt_number",
            name="uq_evaluation_attempt_number"
        ),
        CheckConstraint(
            "attempt_number BETWEEN 1 AND 3",
            name="chk_evaluation_attempt_number"
        ),
    )

    attempt_id: Mapped[int] = mapped_column(
        Integer, primary_key=True
    )

    evaluation_id: Mapped[int] = mapped_column(
        ForeignKey("ai_evaluations.evaluation_id", ondelete="CASCADE"),
        nullable=False
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20), nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    error_code: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )