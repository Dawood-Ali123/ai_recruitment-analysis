# User Schemas
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
)

# Job Schemas
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
)

# Job Requirement Schemas
from app.schemas.job_requirement import (
    JobRequirementCreate,
    JobRequirementResponse,
)

# Job HR Access Schemas
from app.schemas.job_hr_access import (
    JobHRAccessCreate,
    JobHRAccessResponse,
)

# Application Schemas
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
    ApplicationResponse,
)

# CV File Schemas
from app.schemas.cv_file import (
    CVFileCreate,
    CVFileResponse,
)

# AI Evaluation Schemas
from app.schemas.ai_evaluation import (
    AIEvaluationResult,
    AIEvaluationResponse,
)

# CV Processing Attempt Schemas
from app.schemas.cv_processing_attempts import (
    CVProcessingAttemptCreate,
    CVProcessingAttemptResponse,
)

# HR Decision Schemas
from app.schemas.hr_decision import (
    HRDecisionCreate,
    HRDecisionResponse,
)

# Email Record Schemas
from app.schemas.email_record import (
    EmailRecordCreate,
    EmailRecordResponse,
)

# Audit Log Schemas
from app.schemas.audit_log import (
    AuditLogCreate,
    AuditLogResponse,
)