from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.audit_log import AuditLog
from app.models.jobs import Job
from app.models.job_hr_access import JobHRAccess
from app.models.application import Application
router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Logs"]
)


@router.get("/jobs/{job_id}")
def get_job_audit_logs(
    job_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Only HR can access audit logs
    if current_user.role != "hr":
        raise HTTPException(
            status_code=403,
            detail="Only HR can access audit logs"
        )

    # Check job exists
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Check HR access to this job
    has_access = (
        job.created_by == current_user.user_id
    )

    if not has_access:
        has_access = db.query(JobHRAccess).filter(
            JobHRAccess.job_id == job_id,
            JobHRAccess.hr_id == current_user.user_id
        ).first() is not None

    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this job"
        )

    # Fetch audit logs for applications belonging to this job
    logs = (
        db.query(AuditLog)
        .join(
            Application,
            AuditLog.application_id==Application.application_id
        )
        .filter(
            Application.job_id==job_id
        )
        .order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "job_id": job_id,
        "total_returned": len(logs),
        "logs": [
            {
                "log_id": log.log_id,
                "application_id": log.application_id,
                "actor_id": log.actor_id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "created_at": log.created_at
            }
            for log in logs
        ]
    }