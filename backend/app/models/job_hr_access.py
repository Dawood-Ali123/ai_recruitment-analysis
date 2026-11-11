from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Identity,
    ForeignKey,
    UniqueConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class JobHRAccess(Base):

    __tablename__ = "job_hr_access"

    __table_args__ = (
        UniqueConstraint(
            "job_id",
            "hr_user_id",
            name="unique_job_hr"
        ),
    )

    access_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    job_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("jobs.job_id", ondelete="RESTRICT"),
        nullable=False
    )

    hr_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False
    )

    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )