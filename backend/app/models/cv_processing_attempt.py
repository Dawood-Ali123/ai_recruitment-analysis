from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Text,
    DateTime,
    Identity,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class CVProcessingAttempt(Base):

    __tablename__ = "cv_processing_attempts"

    __table_args__ = (

        UniqueConstraint(
            "evaluation_id",
            "attempt_number",
            name="unique_evaluation_attempt"
        ),

        CheckConstraint(
            "status IN ('Processing', 'Completed', 'Failed')",
            name="cv_processing_attempts_status_check"
        ),

        CheckConstraint(
            "attempt_number >= 1 AND attempt_number <= 3",
            name="cv_processing_attempts_attempt_number_check"
        ),

        CheckConstraint(
            """
            (status = 'Processing' AND completed_at IS NULL)
            OR
            (status IN ('Completed', 'Failed') AND completed_at IS NOT NULL)
            """,
            name="chk_attempt_completion"
        ),
    )

    attempt_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    evaluation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "ai_evaluations.evaluation_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'Processing'")
    )

    error_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )