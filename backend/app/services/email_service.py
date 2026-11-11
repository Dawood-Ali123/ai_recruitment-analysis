import smtplib
from email.message import EmailMessage
from app.core.config import settings
from datetime import datetime,timezone
from app.models.email_record import EmailRecord
from sqlalchemy.orm import Session
def send_email(
    recipient_email: str,
    subject: str,
    body: str
):
    message = EmailMessage()

    message["From"] = settings.SMTP_EMAIL
    message["To"] = recipient_email
    message["Subject"] = subject

    message.set_content(body)

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT
    ) as server:

        server.starttls()

        server.login(
            settings.SMTP_EMAIL,
            settings.SMTP_PASSWORD
        )

        server.send_message(message)

    return True

MAX_EMAIL_RETRIES = 3


def send_and_record_email(
    db: Session,
    application_id: int,
    recipient_email: str,
    email_type: str,
    subject: str,
    body: str,
    idempotency_key: str
):
    # Check existing email record
    email_record = db.query(EmailRecord).filter(
        EmailRecord.idempotency_key == idempotency_key
    ).first()

    # Already sent: prevent duplicate email
    if email_record and email_record.delivery_status == "Sent":
        return email_record

    # Create new email record
    if email_record is None:
        email_record = EmailRecord(
            application_id=application_id,
            email_type=email_type,
            recipient_email=recipient_email,
            idempotency_key=idempotency_key,
            delivery_status="Pending"
        )

        db.add(email_record)
        db.commit()
        db.refresh(email_record)

    # Check retry limit
    if email_record.retry_count >= MAX_EMAIL_RETRIES:
        raise ValueError("Maximum email retry attempts reached")

    # Try sending email
    while email_record.retry_count < MAX_EMAIL_RETRIES:

        try:
            email_record.delivery_status = "Sending"
            db.commit()

            send_email(
                recipient_email,
                subject,
                body
            )

            email_record.delivery_status = "Sent"
            email_record.sent_at = datetime.now(timezone.utc)

            db.commit()
            db.refresh(email_record)

            return email_record

        except Exception as error:

            db.rollback()

            email_record = db.query(EmailRecord).filter(
                EmailRecord.idempotency_key == idempotency_key
            ).first()

            email_record.delivery_status = "Failed"
            email_record.retry_count += 1

            db.commit()

            print(
                f"Email attempt {email_record.retry_count} failed: {error}"
            )

    raise RuntimeError("Email delivery failed after 3 attempts")