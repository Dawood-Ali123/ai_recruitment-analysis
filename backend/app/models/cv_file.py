from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Boolean,
    DateTime,
    Identity,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    text,
    Text
    
)

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class CVFile(Base):

    __tablename__ = "cv_files"

    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "version",
            name="unique_application_version"
        ),

        CheckConstraint(
            "file_size_bytes > 0",
            name="cv_files_file_size_bytes_check"
        ),

        CheckConstraint(
            "version > 0",
            name="cv_files_version_check"
        ),
    )

    cv_file_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True
    )

    application_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("applications.application_id", ondelete="RESTRICT"),
        nullable=False
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    file_size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    is_current: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true")
    )

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()")
    )

    extracted_text: Mapped[str | None] = mapped_column(
    Text,
    nullable=True
)