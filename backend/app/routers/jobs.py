from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, distinct
from typing import List

from app.db.database import get_db

from app.models.jobs import Job
from app.models.user import User
from app.models.job_requirement import JobRequirement
from app.models.job_hr_access import JobHRAccess
from app.models.application import Application
from app.models.ai_evaluation import AIEvaluation
from app.models.hr_decsion import HRDecision

from app.schemas.job import (
    JobCreate,
    JobResponse,
    JobDetailsResponse,
    JobUpdate
)

from app.schemas.job_requirement import (
    JobRequirementCreate,
    JobRequirementResponse
)

from app.core.dependencies import require_role

from app.services.audit_service import create_audit_log


router = APIRouter(
    prefix="/jobs",
    tags=["Job Management"]
)


# =====================================================
# CREATE JOB
# =====================================================

@router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):

    new_job = Job(
        title=job_data.title,
        description=job_data.description,
        created_by=current_user.user_id,
        status="Draft"
    )

    try:
        db.add(new_job)

        # Generate job_id before creating audit log
        db.flush()

        # Audit Log
        create_audit_log(
            db=db,
            actor_id=current_user.user_id,
            action="JOB_CREATED",
            entity_type="Job",
            entity_id=new_job.job_id,
            details={
                "title": new_job.title,
                "status": new_job.status
            }
        )

        db.commit()
        db.refresh(new_job)

    except Exception:
        db.rollback()
        raise

    return new_job


# =====================================================
# ADD JOB REQUIREMENT
# =====================================================

@router.post(
    "/{job_id}/requirements",
    response_model=JobRequirementResponse,
    status_code=status.HTTP_201_CREATED
)
def add_job_requirement(
    job_id: int,
    requirement_data: JobRequirementCreate,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):

    # Check whether job exists
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check HR access to this job
    has_access = (
        job.created_by == current_user.user_id
        or db.query(JobHRAccess).filter(
            JobHRAccess.job_id == job_id,
            JobHRAccess.hr_user_id == current_user.user_id
        ).first() is not None
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this job"
        )

    # Create job requirement
    new_requirement = JobRequirement(
        job_id=job_id,
        requirement_type=requirement_data.requirement_type,
        requirement_value=requirement_data.requirement_value,
        is_mandatory=requirement_data.is_mandatory,
        minimum_years=requirement_data.minimum_years
    )

    try:
        db.add(new_requirement)
        db.commit()
        db.refresh(new_requirement)

    except Exception:
        db.rollback()
        raise

    return new_requirement


# =====================================================
# GET ALL OPEN JOBS
# =====================================================

@router.get(
    "/",
    response_model=List[JobResponse]
)
def get_all_open_jobs(
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).filter(
        Job.status == "Open"
    ).order_by(
        Job.created_at.desc()
    ).all()

    return jobs


# =====================================================
# GET HR JOBS
# =====================================================

@router.get(
    "/my-jobs",
    response_model=List[JobResponse]
)
def get_hr_jobs(
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):

    jobs = db.query(Job).outerjoin(
        JobHRAccess,
        Job.job_id == JobHRAccess.job_id
    ).filter(
        or_(
            Job.created_by == current_user.user_id,
            JobHRAccess.hr_user_id == current_user.user_id
        )
    ).distinct().order_by(
        Job.created_at.desc()
    ).all()

    return jobs


# =====================================================
# HR DASHBOARD SUMMARY
# =====================================================

@router.get("/dashboard-summary")
def get_hr_dashboard_summary(
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):

    # Get jobs created by or assigned to current HR
    hr_jobs = db.query(Job.job_id).outerjoin(
        JobHRAccess,
        Job.job_id == JobHRAccess.job_id
    ).filter(
        or_(
            Job.created_by == current_user.user_id,
            JobHRAccess.hr_user_id == current_user.user_id
        )
    ).distinct().subquery()

    # Total jobs
    total_jobs = db.query(
        func.count()
    ).select_from(hr_jobs).scalar() or 0

    # Total applications
    total_applications = db.query(
        func.count(distinct(Application.application_id))
    ).filter(
        Application.job_id.in_(
            db.query(hr_jobs.c.job_id)
        )
    ).scalar() or 0

    # Completed AI evaluations
    completed_evaluations = db.query(
        func.count(distinct(AIEvaluation.application_id))
    ).join(
        Application,
        Application.application_id == AIEvaluation.application_id
    ).filter(
        Application.job_id.in_(
            db.query(hr_jobs.c.job_id)
        ),
        AIEvaluation.processing_status == "Completed"
    ).scalar() or 0

    # Shortlisted candidates
    shortlisted_candidates = db.query(
        func.count(distinct(HRDecision.application_id))
    ).join(
        Application,
        Application.application_id == HRDecision.application_id
    ).filter(
        Application.job_id.in_(
            db.query(hr_jobs.c.job_id)
        ),
        HRDecision.decision == "Shortlisted"
    ).scalar() or 0

    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "completed_evaluations": completed_evaluations,
        "shortlisted_candidates": shortlisted_candidates
    }


# =====================================================
# UPDATE JOB STATUS
# =====================================================

@router.patch(
    "/{job_id}/status",
    response_model=JobResponse
)
def update_job_status(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(require_role("hr")),
    db: Session = Depends(get_db)
):

    # Find job
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check HR access
    has_access = (
        job.created_by == current_user.user_id
        or db.query(JobHRAccess).filter(
            JobHRAccess.job_id == job_id,
            JobHRAccess.hr_user_id == current_user.user_id
        ).first() is not None
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this job"
        )

    # Check status provided
    if job_data.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job status is required"
        )

    # Store previous status
    old_status = job.status

    # Update job status
    job.status = job_data.status

    try:
        # Flush changes before audit log
        db.flush()

        # Audit Log
        create_audit_log(
            db=db,
            actor_id=current_user.user_id,
            action="JOB_STATUS_UPDATED",
            entity_type="Job",
            entity_id=job.job_id,
            details={
                "old_status": old_status,
                "new_status": job.status
            }
        )

        db.commit()
        db.refresh(job)

    except Exception:
        db.rollback()
        raise

    return job


# =====================================================
# GET JOB DETAILS
# =====================================================

@router.get(
    "/{job_id}",
    response_model=JobDetailsResponse
)
def get_job_details(
    job_id: int,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(
        Job.job_id == job_id,
        Job.status == "Open"
    ).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    requirements = db.query(JobRequirement).filter(
        JobRequirement.job_id == job_id
    ).all()

    job_data = JobResponse.model_validate(job).model_dump()

    job_data["requirements"] = requirements

    return job_data