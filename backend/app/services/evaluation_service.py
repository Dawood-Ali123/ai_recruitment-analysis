from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime, timezone

import json

from app.models.application import Application
from app.models.jobs import Job
from app.models.job_requirement import JobRequirement
from app.models.cv_file import CVFile
from app.models.ai_evaluation import AIEvaluation
from app.models.ai_evaluation_attempt import AIEvaluationAttempt

from app.services.cv_processing_service import (
    get_application_and_cv,
    create_evaluation
)

from app.services.audit_service import create_audit_log

from app.core.llm import structured_llm
from app.prompts.evaluation_prompt import evaluation_prompt
from app.schemas.evaluation_report import EvaluationReport
from app.core.config import settings


MAX_EVALUATION_ATTEMPTS = 3


# =====================================================
# GET EVALUATION ATTEMPT COUNT
# =====================================================

def get_evaluation_attempt_count(
    db: Session,
    evaluation_id: int
) -> int:

    return db.query(AIEvaluationAttempt).filter(
        AIEvaluationAttempt.evaluation_id == evaluation_id
    ).count()


# =====================================================
# CREATE EVALUATION ATTEMPT
# =====================================================

def create_evaluation_attempt(
    db: Session,
    evaluation_id: int,
    attempt_number: int
):

    attempt = AIEvaluationAttempt(
        evaluation_id=evaluation_id,
        attempt_number=attempt_number,
        status="Processing",
        started_at=datetime.now(timezone.utc)
    )

    db.add(attempt)
    db.flush()

    return attempt


# =====================================================
# GET EVALUATION CONTEXT
# =====================================================

def get_evaluation_context(
    db: Session,
    application_id: int
):

    # 1. Get application
    application = db.query(Application).filter(
        Application.application_id == application_id
    ).first()

    if application is None:
        raise ValueError("Application not found")

    # 2. Get job
    job = db.query(Job).filter(
        Job.job_id == application.job_id
    ).first()

    if job is None:
        raise ValueError("Job not found")

    # 3. Get job requirements
    requirements = db.query(JobRequirement).filter(
        JobRequirement.job_id == job.job_id
    ).all()

    # 4. Get current CV
    cv_file = db.query(CVFile).filter(
        CVFile.application_id == application_id,
        CVFile.is_current == True
    ).first()

    if cv_file is None:
        raise ValueError("No current CV found")

    # 5. Get extracted CV text
    cv_text = cv_file.extracted_text

    if not cv_text:
        raise ValueError(
            "CV has not been processed yet. Process CV first."
        )

    # 6. Return evaluation data
    return {
        "application_id": application.application_id,
        "job_title": job.title,
        "job_description": job.description,
        "requirements": requirements,
        "cv_text": cv_text
    }


# =====================================================
# FORMAT JOB REQUIREMENTS
# =====================================================

def format_job_requirements(requirements):

    formatted_requirements = []

    for req in requirements:

        formatted_requirements.append({
            "requirement_id": req.requirement_id,
            "type": req.requirement_type,
            "value": req.requirement_value,
            "mandatory": req.is_mandatory,
            "minimum_years": req.minimum_years
        })

    return formatted_requirements


# =====================================================
# EVALUATE CANDIDATE
# =====================================================

def evaluate_candidate(
    db: Session,
    application_id: int
):

    # 1. Get application, job and CV data
    context = get_evaluation_context(
        db,
        application_id
    )

    # 2. Format job requirements
    requirements = format_job_requirements(
        context["requirements"]
    )

    # 3. Prepare prompt variables
    prompt_data = {
        "job_title": context["job_title"],
        "job_description": context["job_description"],
        "job_requirements": json.dumps(
            requirements,
            indent=2,
            default=str
        ),
        "cv_text": context["cv_text"]
    }

    # 4. Generate prompt
    messages = evaluation_prompt.format_messages(
        **prompt_data
    )

    # 5. Get structured AI response
    evaluation_report = structured_llm.invoke(messages)

    score = calculate_overall_score(
        evaluation_report
    )

    evaluation_report = evaluation_report.model_copy(
        update={
            "overall_score": score
        }
    )

    return evaluation_report


# =====================================================
# SAVE EVALUATION REPORT
# =====================================================

def save_evaluation_report(
    db: Session,
    evaluation_id: int,
    report: EvaluationReport
):

    # 1. Find evaluation record
    evaluation = db.query(AIEvaluation).filter(
        AIEvaluation.evaluation_id == evaluation_id
    ).first()

    if evaluation is None:
        raise ValueError("Evaluation not found")

    # 2. Convert report into JSON-compatible dictionary
    evaluation.report = report.model_dump(mode="json")

    # 3. Save overall score
    if report.overall_score is None:
        raise ValueError("Evaluation score is missing")

    evaluation.score = Decimal(
        str(report.overall_score)
    )

    # 4. Update processing information
    evaluation.processing_status = "Completed"

    evaluation.completed_at = datetime.now(timezone.utc)

    evaluation.model_name = settings.GROQ_MODEL

    evaluation.prompt_version = "v1"

    # 5. Create completion audit log
    create_audit_log(
        db=db,
        application_id=evaluation.application_id,
        action="AI_EVALUATION_COMPLETED",
        entity_type="AIEvaluation",
        entity_id=evaluation.evaluation_id,
        details={
            "score": float(evaluation.score),
            "recommendation": report.recommendation,
            "model_name": evaluation.model_name,
            "prompt_version": evaluation.prompt_version,
            "processing_status": "Completed"
        }
    )

    # 6. Commit evaluation and audit log together
    db.commit()

    db.refresh(evaluation)

    return evaluation


# =====================================================
# CALCULATE OVERALL SCORE
# =====================================================

def calculate_overall_score(
    report: EvaluationReport
) -> float:

    all_assessments = (
        report.skills
        + report.education
        + report.experience
    )

    if not all_assessments:
        raise ValueError(
            "No requirements available for scoring"
        )

    matched_count = sum(
        1
        for item in all_assessments
        if item.status == "Matched"
    )

    total_count = len(all_assessments)

    score = (
        matched_count / total_count
    ) * 100

    return round(score, 2)


# =====================================================
# RUN CANDIDATE EVALUATION
# =====================================================

def run_candidate_evaluation(
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

    if evaluation is None:
        raise ValueError(
            "CV processing must be completed first"
        )

    if evaluation.processing_status == "Completed":
        raise ValueError(
            "This CV has already been evaluated"
        )

    if evaluation.processing_status == "Processing":
        raise ValueError(
            "Evaluation is already in progress"
        )

    if not cv_file.extracted_text:
        raise ValueError(
            "CV has not been processed yet"
        )

    evaluation_id = evaluation.evaluation_id

    # 3. Get previous attempts
    previous_attempts = get_evaluation_attempt_count(
        db,
        evaluation_id
    )

    if previous_attempts >= MAX_EVALUATION_ATTEMPTS:
        raise ValueError(
            "Maximum evaluation attempts reached"
        )

    # 4. Mark evaluation as processing
    evaluation.processing_status = "Processing"

    # 5. Audit: Evaluation Started
    create_audit_log(
        db=db,
        application_id=application_id,
        action="AI_EVALUATION_STARTED",
        entity_type="AIEvaluation",
        entity_id=evaluation_id,
        details={
            "cv_file_id": cv_file.cv_file_id,
            "previous_attempts": previous_attempts,
            "maximum_attempts": MAX_EVALUATION_ATTEMPTS,
            "processing_status": "Processing"
        }
    )

    db.commit()

    # 6. Run evaluation with retry
    for attempt_number in range(
        previous_attempts + 1,
        MAX_EVALUATION_ATTEMPTS + 1
    ):

        attempt = create_evaluation_attempt(
            db,
            evaluation_id,
            attempt_number
        )

        attempt_id = attempt.attempt_id

        evaluation = db.query(AIEvaluation).filter(
            AIEvaluation.evaluation_id == evaluation_id
        ).first()

        evaluation.processing_status = "Processing"

        db.commit()

        try:

            # 7. Run AI evaluation
            report = evaluate_candidate(
                db,
                application_id
            )

            # 8. Save evaluation report
            saved_evaluation = save_evaluation_report(
                db,
                evaluation_id,
                report
            )

            # 9. Mark attempt completed
            attempt = db.query(AIEvaluationAttempt).filter(
                AIEvaluationAttempt.attempt_id == attempt_id
            ).first()

            attempt.status = "Completed"

            attempt.completed_at = datetime.now(timezone.utc)

            db.commit()

            return {
                "message": "AI evaluation completed successfully",
                "evaluation_id": evaluation_id,
                "attempt_number": attempt_number,
                "score": float(saved_evaluation.score),
                "processing_status": "Completed",
                "report": saved_evaluation.report
            }

        except Exception as error:

            # 10. Rollback failed transaction
            db.rollback()

            # 11. Reload attempt
            attempt = db.query(AIEvaluationAttempt).filter(
                AIEvaluationAttempt.attempt_id == attempt_id
            ).first()

            evaluation = db.query(AIEvaluation).filter(
                AIEvaluation.evaluation_id == evaluation_id
            ).first()

            # 12. Record failed attempt
            attempt.status = "Failed"

            attempt.completed_at = datetime.now(timezone.utc)

            attempt.error_code = type(error).__name__

            attempt.error_message = str(error)[:2000]

            # 13. Update evaluation status
            is_final_attempt = (
                attempt_number == MAX_EVALUATION_ATTEMPTS
            )

            evaluation.processing_status = (
                "Failed"
                if is_final_attempt
                else "Pending"
            )

            # 14. Audit: Attempt Failed
            create_audit_log(
                db=db,
                application_id=application_id,
                action="AI_EVALUATION_ATTEMPT_FAILED",
                entity_type="AIEvaluation",
                entity_id=evaluation_id,
                details={
                    "attempt_number": attempt_number,
                    "error_code": type(error).__name__,
                    "processing_status": evaluation.processing_status
                }
            )

            # 15. Audit: Final Evaluation Failed
            if is_final_attempt:

                create_audit_log(
                    db=db,
                    application_id=application_id,
                    action="AI_EVALUATION_FAILED",
                    entity_type="AIEvaluation",
                    entity_id=evaluation_id,
                    details={
                        "maximum_attempts": MAX_EVALUATION_ATTEMPTS,
                        "error_code": type(error).__name__,
                        "processing_status": "Failed"
                    }
                )

            db.commit()

    raise RuntimeError(
        "AI evaluation failed after all attempts"
    )