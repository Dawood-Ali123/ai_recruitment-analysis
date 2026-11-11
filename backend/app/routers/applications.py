from fastapi import APIRouter,Depends,HTTPException,status,UploadFile,File
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.jobs import Job
from app.models.application import Application
from app.models.user import User
from app.models.ai_evaluation import AIEvaluation
from app.schemas.application import ApplicationCreate,ApplicationResponse
from app.models.job_hr_access import JobHRAccess
from app.schemas.application import HRApplicationResponse
import os
from app.core.dependencies import require_role
import uuid
from pathlib import Path
from fastapi import UploadFile,File
from sqlalchemy import func
from app.models.cv_file import CVFile
from app.schemas.cv_file import CVFileResponse
import io 
import zipfile
import re
from app.core.paths import CV_STORAGE_DIR
from app.models.jobs import Job
from app.models.job_hr_access import JobHRAccess
from app.services.evaluation_service import run_candidate_evaluation
from app.services.cv_processing_service import process_cv
from app.models.hr_decsion import HRDecision
from app.schemas.hr_decision import HRDecisionResponse,HRDecisionCreate
from app.services.email_service import send_and_record_email
from fastapi.responses import FileResponse
from app.services.audit_service import create_audit_log
def verify_hr_job_access(
    db: Session,
    job_id: int,
    hr_user_id: int
):
    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Check whether HR created this job
    if job.created_by == hr_user_id:
        return job

    # Check whether HR has assigned access
    access = db.query(JobHRAccess).filter(
        JobHRAccess.job_id == job_id,
        JobHRAccess.hr_user_id == hr_user_id
    ).first()

    if access is None:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this job"
        )

    return job
def get_next_cv_version(
    db: Session,
    application_id: int
):

    latest_version = db.query(
        func.max(CVFile.version)
    ).filter(
        CVFile.application_id == application_id
    ).scalar()

    return (latest_version or 0) + 1

def sanitize_filename(filename: str) -> str:

    filename = Path(filename).name

    filename = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        filename
    )

    return filename[:255]

def validate_cv_file(file: UploadFile):

    allowed_extensions = {".pdf", ".docx"}

    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are allowed"
        )

    allowed_mime_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }

    if file.content_type not in allowed_mime_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file content type"
        )

async def validate_file_signature(file: UploadFile):

    file_header = await file.read(8)
#file kay starting ki 8 bytes read krta ha
    await file.seek(0)
#agar reset nahi kariengy to save_cv_files() k starting content nahi mily ga
    if file.filename.lower().endswith(".pdf"):

        if not file_header.startswith(b"%PDF-"):
#check krta ha ky actual file pdf signature sae start ho rahi ha kay nahi
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid PDF file content"
            )

    elif file.filename.lower().endswith(".docx"):

        if not file_header.startswith(b"PK"):
#check krta ha DOCX zip container hoti ha isliya uski zip signature check krta ha
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid DOCX file content"
            )

async def save_cv_file(file: UploadFile):

    CV_STORAGE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    file_extension = Path(file.filename).suffix.lower()

    unique_filename = f"{uuid.uuid4()}{file_extension}"

    file_path = CV_STORAGE_DIR / unique_filename

    temp_path = CV_STORAGE_DIR / f".{unique_filename}.tmp"

    max_file_size = 5 * 1024 * 1024
    total_size = 0

    try:

        with open(temp_path, "wb") as buffer:

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > max_file_size:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="CV file size must not exceed 5 MB"
                    )

                buffer.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty"
            )

        # Move Temporary File to Final Location
        os.replace(temp_path, file_path)

        return unique_filename, total_size

    except Exception:

        if temp_path.exists():
            temp_path.unlink()

        if file_path.exists():
            file_path.unlink()

        raise

async def validate_docx_package(file: UploadFile):

    max_file_size = 5 * 1024 * 1024

    # Check Uploaded File Size
    

    file_size = file.size
    if file_size is None:
        await file.seek(0)
        content=await file.read()
        file_size=len(content)
        await file.seek(0)


    if file_size > max_file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="CV file size must not exceed 5 MB"
        )

    content = await file.read()

    await file.seek(0)

    try:
        with zipfile.ZipFile(io.BytesIO(content)) as docx:

            # Check Number of Files
            if len(docx.infolist()) > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="DOCX contains too many files"
                )

            # Check Extracted Content Size
            total_uncompressed_size = sum(
                info.file_size for info in docx.infolist()
            )

            if total_uncompressed_size > 20 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="DOCX extracted content is too large"
                )

            # Check Required DOCX Files
            required_files = {
                "[Content_Types].xml",
                "word/document.xml"
            }

            available_files = set(docx.namelist())

            if not required_files.issubset(available_files):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid DOCX document structure"
                )

    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid DOCX file"
        )
router=APIRouter(
    prefix="/applications",
    tags=['Applications']
)

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
def apply_for_job(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check Candidate Role
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can apply for jobs"
        )

    # Check Job Exists and s Open
    job = db.query(Job).filter(
        Job.job_id == application_data.job_id,
        Job.status == "Open"
    ).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not open"
        )

    # Check Duplicate Application
    existing_application = db.query(Application).filter(
        Application.candidate_id == current_user.user_id,
        Application.job_id == application_data.job_id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied for this job"
        )

    # Create Application
    new_application = Application(
        candidate_id=current_user.user_id,
        job_id=application_data.job_id,
        status="Submitted"
    )
    db.add(new_application)
    db.flush()
    create_audit_log(
        db=db,
        actor_id=current_user.user_id,
        application_id=new_application.application_id,
        action="APPLICATION_SUBMITTED",
        entity_type="Application",
        entity_id=new_application.application_id,
        details={
            "job_id": new_application.job_id,
            "status": new_application.status
        }
    )
    db.commit()
    db.refresh(new_application)

    return new_application
@router.get("/my-jobs")
def get_my_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hr"))
):
    # Existing my-jobs endpoint code
    pass


@router.get(
    "/jobs/{job_id}/applications",
    response_model=list[HRApplicationResponse]
)
def get_job_applications(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Check HR Role
    if current_user.role != "hr":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only HR can view job applications"
        )

    # Check Job Access
    job = db.query(Job).filter(
        Job.job_id == job_id,
        (
            (Job.created_by == current_user.user_id) |
            (
                Job.job_id.in_(
                    db.query(JobHRAccess.job_id).filter(
                        JobHRAccess.hr_user_id == current_user.user_id
                    )
                )
            )
        )
    ).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or you don't have access"
        )

    # Get Applications with Candidate Information
    applications = db.query(
        Application,
        User.full_name,
        User.email
    ).join(
        User,
        Application.candidate_id == User.user_id
    ).filter(
        Application.job_id == job_id
    ).order_by(
        Application.created_at.desc()
    ).all()

    # Prepare Response
    result = []

    for application, candidate_name, candidate_email in applications:

        application_data = HRApplicationResponse(
            application_id=application.application_id,
            candidate_id=application.candidate_id,
            job_id=application.job_id,
            status=application.status,
            created_at=application.created_at,
            updated_at=application.updated_at,
            candidate_name=candidate_name,
            candidate_email=candidate_email
        )

        result.append(application_data)

    return result

@router.post(
    "/{application_id}/upload-cv",
    response_model=CVFileResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_cv(
    application_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 1. Check Candidate Role
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can upload CV"
        )

    # 2. Check Application Ownership
    application = db.query(Application).filter(
        Application.application_id == application_id,
        Application.candidate_id == current_user.user_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # 3. Validate CV
    validate_cv_file(file)
    await validate_file_signature(file)
    if file.filename.lower().endswith(".docx"):
        await validate_docx_package(file)
    # 4. Calculate CV Version
    version = get_next_cv_version(
        db,
        application_id
    )

    # 5. Save CV File
    storage_key, file_size = await save_cv_file(file)
    try:
        db.query(CVFile).filter(
            CVFile.application_id==application_id
        ).update(
            {
                CVFile.is_current:False
            }
        )

        new_cv=CVFile(
            application_id=application_id,
            original_filename=sanitize_filename(file.filename),
            storage_key=storage_key,
            mime_type=file.content_type,
            file_size_bytes=file_size,
            version=version,
            is_current=True
        )
        db.add(new_cv)
        db.flush()

        create_audit_log(
    db=db,
    actor_id=current_user.user_id,
    application_id=application_id,
    action="CV_UPLOADED",
    entity_type="CVFile",
    entity_id=new_cv.cv_file_id,
    details={
        "filename": new_cv.original_filename,
        "version": new_cv.version,
        "file_size_bytes": new_cv.file_size_bytes
    }
)
        db.commit()
    except Exception:
        db.rollback()

        file_path=CV_STORAGE_DIR/storage_key
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save CV information"
        )
    db.refresh(new_cv)
    return new_cv


@router.post("/{application_id}/evaluate")
def trigger_ai_evaluation(
    application_id:int,
    db:Session=Depends(get_db),
    current_user:User=Depends(require_role("hr"))
):
    application=db.query(Application).filter(
        Application.application_id==application_id
    ).first()
    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )
    verify_hr_job_access(
        db,
        application.job_id,
        current_user.user_id
    )
    result=run_candidate_evaluation(
        db,
        application_id
    )
    return result

@router.post("/{application_id}/process-cv")
def trigger_cv_processing(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hr"))
):
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    verify_hr_job_access(
        db,
        application.job_id,
        current_user.user_id
    )

    try:
        result = process_cv(db, application_id)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

@router.get("/{application_id}/evaluation")
def get_application_evaluation(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hr"))
):

    # 1. Find application
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    # 2. Verify HR permission
    verify_hr_job_access(
        db,
        application.job_id,
        current_user.user_id
    )

    # 3. Find current CV
    cv_file = db.query(CVFile).filter(
        CVFile.application_id == application_id,
        CVFile.is_current == True
    ).first()

    if cv_file is None:
        raise HTTPException(
            status_code=404,
            detail="No CV found"
        )

    # 4. Find latest evaluation for current CV
    evaluation = db.query(AIEvaluation).filter(
        AIEvaluation.application_id == application_id,
        AIEvaluation.cv_file_id == cv_file.cv_file_id
    ).order_by(
        AIEvaluation.evaluation_id.desc()
    ).first()

    if evaluation is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation not found"
        )

    # 5. Check evaluation status
    if evaluation.processing_status != "Completed":
        return {
            "application_id": application_id,
            "evaluation_id": evaluation.evaluation_id,
            "processing_status": evaluation.processing_status,
            "message": "Evaluation is not completed yet"
        }

    # 6. Return saved report
    return {
        "application_id": application_id,
        "evaluation_id": evaluation.evaluation_id,
        "processing_status": evaluation.processing_status,
        "score": float(evaluation.score) if evaluation.score is not None else None,
        "model_name": evaluation.model_name,
        "report": evaluation.report
    }



@router.post(
    "/{application_id}/decision",
    response_model=HRDecisionResponse
)
def create_hr_decision(
    application_id: int,
    decision_data: HRDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hr"))
):
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    verify_hr_job_access(
        db,
        application.job_id,
        current_user.user_id
    )

    evaluation = db.query(AIEvaluation).filter(
        AIEvaluation.application_id == application_id,
        AIEvaluation.processing_status == "Completed"
    ).order_by(
        AIEvaluation.evaluation_id.desc()
    ).first()

    if evaluation is None:
        raise HTTPException(
            status_code=400,
            detail="Candidate must be evaluated before HR decision"
        )

    # Get candidate email
    candidate = db.query(User).filter(
        User.user_id == application.candidate_id
    ).first()

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    # Save HR decision
    hr_decision = HRDecision(
        application_id=application_id,
        decided_by=current_user.user_id,
        decision=decision_data.decision,
        notes=decision_data.notes
    )

    db.add(hr_decision)
    db.flush()
    create_audit_log(
    db=db,
    actor_id=current_user.user_id,
    application_id=application_id,
    action="HR_DECISION_RECORDED",
    entity_type="HRDecision",
    entity_id=hr_decision.decision_id,
    details={
        "decision": hr_decision.decision
    }
)

    db.commit()
    db.refresh(hr_decision)

    # Prepare email
    subject = f"Application Update - {decision_data.decision}"

    body = f"""
Dear Candidate,

Your application status has been updated.

Decision: {decision_data.decision}

HR Notes: {decision_data.notes or "No additional notes."}

Thank you for applying.

Regards,
HR Team
AI Recruitment Platform
"""

    print("STEP 1: HR decision saved")
    print("STEP 2: Candidate email:", candidate.email)

    try:
        print("STEP 3: Calling email service")

        result = send_and_record_email(
            db=db,
            application_id=application_id,
            recipient_email=candidate.email,
            email_type=decision_data.decision,
            subject=subject,
            body=body,
            idempotency_key=f"decision_{hr_decision.decision_id}"
        )

        print("STEP 4: Email result:", result.delivery_status)

    except Exception as error:
        print("EMAIL ERROR:", repr(error))

    print("STEP 5: Email process finished")

    return hr_decision

@router.get(
    "/",
    response_model=list[ApplicationResponse]
)
def get_my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only candidates can view their applications
    if current_user.role != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only candidates can view their applications"
        )

    # Fetch applications belonging to logged-in candidate
    applications = db.query(Application).filter(
        Application.candidate_id == current_user.user_id
    ).order_by(
        Application.created_at.desc()
    ).all()

    return applications

@router.get("/my-tracking")
def get_my_application_tracking(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("candidate"))
):
    # Only logged-in candidate's applications
    applications = db.query(Application).filter(
        Application.candidate_id == current_user.user_id
    ).order_by(
        Application.created_at.desc()
    ).all()

    tracking_data = []

    for application in applications:

        # Get job information
        job = db.query(Job).filter(
            Job.job_id == application.job_id
        ).first()

        # Get current CV
        cv_file = db.query(CVFile).filter(
            CVFile.application_id == application.application_id,
            CVFile.is_current == True
        ).first()

        # Get latest evaluation for current CV
        evaluation = None

        if cv_file:
            evaluation = db.query(AIEvaluation).filter(
                AIEvaluation.application_id == application.application_id,
                AIEvaluation.cv_file_id == cv_file.cv_file_id
            ).order_by(
                AIEvaluation.evaluation_id.desc()
            ).first()

        # Get latest HR decision
        hr_decision = db.query(HRDecision).filter(
            HRDecision.application_id == application.application_id
        ).order_by(
            HRDecision.created_at.desc()
        ).first()

        # Extract recommendation safely
        recommendation = None

        if evaluation and evaluation.report:
            recommendation = evaluation.report.get("recommendation")

        tracking_data.append({
            "application_id": application.application_id,
            "job_id": application.job_id,
            "job_title": job.title if job else "Unknown Job",
            "application_status": application.status,
            "applied_at": application.created_at,

            "cv": {
                "uploaded": cv_file is not None,
                "filename": cv_file.original_filename if cv_file else None,
                "version": cv_file.version if cv_file else None
            },

            "ai_evaluation": {
                "status": evaluation.processing_status if evaluation else "Not Started",
                "score": float(evaluation.score) if evaluation and evaluation.score is not None else None,
                "recommendation": recommendation
            },

            "hr_decision": {
                "decision": hr_decision.decision if hr_decision else None,
                "decision_date": hr_decision.created_at if hr_decision else None
            }
        })

    return tracking_data


@router.get("/{application_id}/details")
def get_application_details(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hr"))
):
    # 1. Find application
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    # 2. Verify HR access
    verify_hr_job_access(
        db,
        application.job_id,
        current_user.user_id
    )

    # 3. Get candidate information
    candidate = db.query(User).filter(
        User.user_id == application.candidate_id
    ).first()

    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    # 4. Get job information
    job = db.query(Job).filter(
        Job.job_id == application.job_id
    ).first()

    # 5. Get current CV
    cv_file = db.query(CVFile).filter(
        CVFile.application_id == application_id,
        CVFile.is_current == True
    ).first()

    # 6. Prepare CV information
    cv_data = None

    if cv_file:
        cv_data = {
            "cv_file_id": cv_file.cv_file_id,
            "filename": cv_file.original_filename,
            "mime_type": cv_file.mime_type,
            "file_size_bytes": cv_file.file_size_bytes,
            "version": cv_file.version,
            "uploaded_at": cv_file.uploaded_at,
            "is_current": cv_file.is_current
        }

    # 7. Return application details
    return {
        "application_id": application.application_id,
        "status": application.status,
        "created_at": application.created_at,
        "updated_at": application.updated_at,

        "candidate": {
            "candidate_id": candidate.user_id,
            "full_name": candidate.full_name,
            "email": candidate.email
        },

        "job": {
            "job_id": job.job_id,
            "title": job.title,
            "description": job.description
        },

        "cv": cv_data
    }


@router.get("/{application_id}/cv")
def get_application_cv(
    application_id: int,
    download: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("hr"))
):
    # 1. Find application
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    # 2. Verify HR access
    verify_hr_job_access(
        db,
        application.job_id,
        current_user.user_id
    )

    # 3. Get current CV
    cv_file = db.query(CVFile).filter(
        CVFile.application_id == application_id,
        CVFile.is_current == True
    ).first()

    if cv_file is None:
        raise HTTPException(
            status_code=404,
            detail="CV not found"
        )

    # 4. Resolve secure file path
    storage_directory = CV_STORAGE_DIR.resolve()

    file_path = (
        storage_directory / cv_file.storage_key
    ).resolve()

    # Prevent path traversal
    if not file_path.is_relative_to(storage_directory):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path"
        )

    # 5. Check physical file
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="CV file does not exist in storage"
        )

    # 6. Return CV
    return FileResponse(
        path=file_path,
        media_type=cv_file.mime_type,
        filename=cv_file.original_filename,
        content_disposition_type=(
            "attachment" if download else "inline"
        )
    )



