from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Numeric,
    Identity,
    ForeignKey,
    CheckConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class JobRequirement(Base):

    __tablename__ = "job_requirements"

    __table_args__ = (
        CheckConstraint(
            "requirement_type IN ('Skill', 'Education', 'Experience')",
            name="job_requirements_requirement_type_check"
        ),
        CheckConstraint(
            "minimum_years IS NULL OR minimum_years >= 0",
            name="chk_minimum_years"
        ),
        CheckConstraint(
            "requirement_type = 'Experience' OR minimum_years IS NULL",
            name="chk_experience_years"
        ),
    )

    requirement_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    job_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("jobs.job_id", ondelete="RESTRICT"),
        nullable=False
    )

    requirement_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    requirement_value: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    is_mandatory: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true")
    )

    minimum_years: Mapped[Decimal | None] = mapped_column(
        Numeric,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )