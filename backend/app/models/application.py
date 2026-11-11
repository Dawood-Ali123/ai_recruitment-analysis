from datetime import datetime

from sqlalchemy import (
    BigInteger,
    String,
    DateTime,
    Identity,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Application(Base):

    __tablename__ = "applications"

    __table_args__ = (
        UniqueConstraint(
            "candidate_id",
            "job_id",
            name="unique_candidate_job"
        ),

        CheckConstraint(
            """
            status IN (
                'Submitted',
                'Processing',
                'Needs Review',
                'HR Review',
                'Shortlisted',
                'Rejected',
                'Withdrawn'
            )
            """,
            name="applications_status_check"
        ),
    )

    application_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    candidate_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    job_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("jobs.job_id", ondelete="RESTRICT"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        server_default=text("'Submitted'")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )