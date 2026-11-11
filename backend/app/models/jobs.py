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


class Job(Base):

    __tablename__ = "jobs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('Draft', 'Open', 'Closed', 'Archived')",
            name="jobs_status_check"
        ),
    )

    job_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.user_id",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'Draft'")
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