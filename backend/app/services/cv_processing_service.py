from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.cv_file import CVFile
from app.models.ai_evaluation import AIEvaluation
from app.models.cv_processing_attempt import CVProcessingAttempt

from app.services.cv_extractor import extract_cv_text
from app.services.audit_service import create_audit_log

from app.core.paths import CV_STORAGE_DIR


MAX_PROCESSING_ATTEMPTS = 3


# =====================================================
# GET APPLICATION AND CURRENT CV
# =====================================================

def get_application_and_cv(
    db: Session,
    application_id: int
):
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise ValueError("Application Not found")

    cv_file = db.query(CVFile).filter(
        CVFile.application_id == application_id,
        CVFile.is_current == True
    ).first()

    if cv_file is None:
        raise ValueError("No CV uploaded for this application")

    return application, cv_file


# =====================================================
# CREATE EVALUATION
# =====================================================

def create_evaluation(
    db: Session,
    application: Application,
    cv_file: CVFile
):
    evaluation = AIEvaluation(
        application_id=application.application_id,
        cv_file_id=cv_file.cv_file_id,
        processing_status="Pending"
    )

    db.add(evaluation)
    db.flush()

    return evaluation


# =====================================================
# CREATE PROCESSING ATTEMPT
# =====================================================

def create_processing_attempt(
    db: Session,
    evaluation: AIEvaluation,
    attempt_number: int
):
    attempt = CVProcessingAttempt(
        evaluation_id=evaluation.evaluation_id,
        attempt_number=attempt_number,
        status="Processing"
    )

    db.add(attempt)
    db.flush()

    return attempt


# =====================================================
# GET PROCESSING ATTEMPT COUNT
# =====================================================

def get_processing_attempt_count(
    db: Session,
    evaluation_id: int
) -> int:

    count = db.query(CVProcessingAttempt).filter(
        CVProcessingAttempt.evaluation_id == evaluation_id
    ).count()

    return count


# =====================================================
# EXTRACT APPLICATION CV
# =====================================================

def extract_application_cv(
    cv_file: CVFile
) -> str:

    file_path = CV_STORAGE_DIR / cv_file.storage_key

    if not file_path.exists():
        raise FileNotFoundError("CV file not found in storage")

    extracted_text = extract_cv_text(str(file_path))

    return extracted_text


# =====================================================
# MARK PROCESSING SUCCESS
# =====================================================

def mark_processing_success(
    db: Session,
    evaluation: AIEvaluation,
    attempt: CVProcessingAttempt
):

    current_time = datetime.now(timezone.utc)

    attempt.status = "Completed"
    attempt.completed_at = current_time

    evaluation.processing_status = "Pending"

    db.flush()


# =====================================================
# PROCESS CV WITH RETRY
# =====================================================

def process_cv_with_retry(
    db: Session,
    evaluation_id: int,
    cv_file_id: int,
    application_id: int
) -> str:

    # Get previous attempts
    previous_attempts = get_processing_attempt_count(
        db,
        evaluation_id
    )

    for attempt_number in range(
        previous_attempts + 1,
        MAX_PROCESSING_ATTEMPTS + 1
    ):

        # 1. Get evaluation
        evaluation = db.query(AIEvaluation).filter(
            AIEvaluation.evaluation_id == evaluation_id
        ).first()

        if evaluation is None:
            raise ValueError("Evaluation not found")

        # 2. Create processing attempt
        attempt = create_processing_attempt(
            db,
            evaluation,
            attempt_number
        )

        attempt_id = attempt.attempt_id

        db.commit()

        try:

            # 3. Get current CV file
            cv_file = db.query(CVFile).filter(
                CVFile.cv_file_id == cv_file_id
            ).first()

            if cv_file is None:
                raise ValueError("CV file not found")

            # 4. Extract CV text
            extracted_text = extract_application_cv(cv_file)

            # 5. Save extracted text
            cv_file.extracted_text = extracted_text

            # 6. Mark attempt successful
            attempt.status = "Completed"
            attempt.completed_at = datetime.now(timezone.utc)

            evaluation.processing_status = "Pending"

            db.commit()

            return extracted_text

        except Exception as error:

            # 7. Rollback failed transaction
            db.rollback()

            # 8. Reload records
            evaluation = db.query(AIEvaluation).filter(
                AIEvaluation.evaluation_id == evaluation_id
            ).first()

            attempt = db.query(CVProcessingAttempt).filter(
                CVProcessingAttempt.attempt_id == attempt_id
            ).first()

            application = db.query(Application).filter(
                Application.application_id == application_id
            ).first()

            # 9. Record failed attempt
            attempt.status = "Failed"
            attempt.completed_at = datetime.now(timezone.utc)

            attempt.error_code = type(error).__name__
            attempt.error_message = str(error)[:2000]

            # 10. Check maximum attempts
            if attempt_number == MAX_PROCESSING_ATTEMPTS:

                evaluation.processing_status = "Failed"
                application.status = "Needs Review"

            else:

                evaluation.processing_status = "Pending"

            db.commit()

    raise RuntimeError(
        "CV processing failed after all attempts"
    )


# =====================================================
# MARK PROCESSING FAILURE
# =====================================================

def mark_processing_failure(
    db: Session,
    application: Application,
    evaluation: AIEvaluation,
    attempt: CVProcessingAttempt,
    error: Exception
):

    current_time = datetime.now(timezone.utc)

    attempt.status = "Failed"
    attempt.completed_at = current_time

    evaluation.processing_status = "Failed"

    attempt.error_code = type(error).__name__
    attempt.error_message = str(error)[:2000]

    application.status = "Needs Review"

    db.flush()


# =====================================================
# PROCESS CV
# =====================================================

def process_cv(
    db: Session,
    application_id: int
):

    # 1. Get application and current CV
    application, cv_file = get_application_and_cv(
        db,
        application_id
    )

    # 2. Find existing evaluation
    evaluation = db.query(AIEvaluation).filter(
        AIEvaluation.application_id == application_id,
        AIEvaluation.cv_file_id == cv_file.cv_file_id
    ).order_by(
        AIEvaluation.evaluation_id.desc()
    ).first()

    # 3. Check existing evaluation
    if evaluation:

        if evaluation.processing_status in [
            "Processing",
            "Completed"
        ]:
            raise ValueError(
                "CV is already being processed or evaluated"
            )

        if cv_file.extracted_text:
            raise ValueError(
                "CV has already been processed"
            )

        # Check previous attempts
        attempt_count = get_processing_attempt_count(
            db,
            evaluation.evaluation_id
        )

        if attempt_count >= MAX_PROCESSING_ATTEMPTS:
            raise ValueError(
                "Maximum processing attempts reached"
            )

    else:

        # 4. Create evaluation only if it doesn't exist
        evaluation = create_evaluation(
            db,
            application,
            cv_file
        )

    evaluation_id = evaluation.evaluation_id

    try:

        # 5. Update application status
        application.status = "Processing"
        evaluation.processing_status = "Processing"

        # 6. Audit: Processing Started
        create_audit_log(
            db=db,
            application_id=application_id,
            action="CV_PROCESSING_STARTED",
            entity_type="CVFile",
            entity_id=cv_file.cv_file_id,
            details={
                "evaluation_id": evaluation_id,
                "processing_status": "Processing"
            }
        )

        db.commit()

        # 7. Process CV with retry
        process_cv_with_retry(
            db=db,
            evaluation_id=evaluation_id,
            cv_file_id=cv_file.cv_file_id,
            application_id=application_id
        )

        # 8. Reload records
        application = db.query(Application).filter(
            Application.application_id == application_id
        ).first()

        evaluation = db.query(AIEvaluation).filter(
            AIEvaluation.evaluation_id == evaluation_id
        ).first()

        # 9. Audit: Processing Completed
        create_audit_log(
            db=db,
            application_id=application_id,
            action="CV_PROCESSING_COMPLETED",
            entity_type="CVFile",
            entity_id=cv_file.cv_file_id,
            details={
                "evaluation_id": evaluation_id,
                "processing_status": "Completed"
            }
        )

        db.commit()

        return {
            "message": "CV processed successfully",
            "application_id": application_id,
            "evaluation_id": evaluation_id,
            "processing_status": "Pending"
        }

    except Exception as error:

        # 10. Rollback failed transaction
        db.rollback()

        # 11. Reload records
        application = db.query(Application).filter(
            Application.application_id == application_id
        ).first()

        evaluation = db.query(AIEvaluation).filter(
            AIEvaluation.evaluation_id == evaluation_id
        ).first()

        if application and evaluation:

            application.status = "Needs Review"
            evaluation.processing_status = "Failed"

            # 12. Audit: Processing Failed
            create_audit_log(
                db=db,
                application_id=application_id,
                action="CV_PROCESSING_FAILED",
                entity_type="CVFile",
                entity_id=cv_file.cv_file_id,
                details={
                    "evaluation_id": evaluation_id,
                    "processing_status": "Failed",
                    "error_code": type(error).__name__
                }
            )

            db.commit()

        return {
            "message": "CV processing failed",
            "application_id": application_id,
            "evaluation_id": evaluation_id,
            "processing_status": "Failed",
            "error_code": type(error).__name__
        }