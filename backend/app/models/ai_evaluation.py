from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Numeric,
    Identity,
    ForeignKey,
    CheckConstraint,
    text
)

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class AIEvaluation(Base):

    __tablename__ = "ai_evaluations"

    __table_args__ = (

        CheckConstraint(
            "processing_status IN ('Pending', 'Processing', 'Completed', 'Failed')",
            name="ai_evaluations_processing_status_check"
        ),

        CheckConstraint(
            "score IS NULL OR (score >= 0 AND score <= 100)",
            name="ai_evaluations_score_check"
        ),

        CheckConstraint(
            """
            processing_status != 'Completed'
            OR (
                score IS NOT NULL
                AND report IS NOT NULL
                AND completed_at IS NOT NULL
            )
            """,
            name="chk_completed_evaluation"
        ),
    )

    evaluation_id: Mapped[int] = mapped_column(
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

    cv_file_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "cv_files.cv_file_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    processing_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'Pending'")
    )

    score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True
    )

    report: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    prompt_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )