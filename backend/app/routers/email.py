from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.email_record import EmailRecord
from app.models.application import Application
from app.models.user import User
from app.core.dependencies import require_role
from app.schemas.email_record import EmailRecordResponse

router = APIRouter(prefix="/emails", tags=["Email Notifications"])


@router.get(
    "/applications/{application_id}",
    response_model=list[EmailRecordResponse]
)
def get_application_emails(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hr"))
):
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise HTTPException(404, "Application not found")

    # Verify HR access to this job
    from app.routers.applications import verify_hr_job_access

    verify_hr_job_access(
        db,
        application.job_id,
        current_user.user_id
    )

    emails = db.query(EmailRecord).filter(
        EmailRecord.application_id == application_id
    ).order_by(
        EmailRecord.created_at.desc()
    ).all()

    return emails