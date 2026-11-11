from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    DateTime,
    Identity,
    ForeignKey,
    CheckConstraint,
    text
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class EmailRecord(Base):

    __tablename__ = "email_records"

    __table_args__ = (

        CheckConstraint(
            "delivery_status IN ('Pending', 'Sending', 'Sent', 'Failed')",
            name="email_records_delivery_status_check"
        ),

        CheckConstraint(
            "retry_count >= 0 AND retry_count <= 3",
            name="email_records_retry_count_check"
        ),

        CheckConstraint(
            """
            (delivery_status = 'Sent' AND sent_at IS NOT NULL)
            OR
            (delivery_status != 'Sent' AND sent_at IS NULL)
            """,
            name="chk_email_sent_at"
        ),
    )

    email_id: Mapped[int] = mapped_column(
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

    email_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    recipient_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    delivery_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=text("'Pending'")
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0")
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    provider_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )