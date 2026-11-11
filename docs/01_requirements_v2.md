# AI-Powered HR Recruitment & CV Screening Platform
## Software Requirements Specification (SRS) — Draft v2

**Document status:** Consolidated working draft  
**Version:** 2.0  
**Purpose:** Define the agreed scope, requirements, business rules, quality expectations, and acceptance criteria before system design and implementation.

> This document captures decisions agreed during requirements-learning sessions. Items listed under **Open Decisions** are intentionally not treated as finalized requirements.

---

## 1. Project Overview

The platform helps an organization manage job openings, receive candidate CVs, evaluate applications against job-specific requirements, and support HR review. AI prepares an evidence-based evaluation; authorized HR users retain responsibility for recruitment decisions.

The system will support candidate application submission and permitted application-status tracking, HR job management, CV processing, AI-assisted screening, human review, shortlist/rejection decisions, interview invitations, candidate emails, audit logging, and secure access control.

## 2. Objectives

1. Make CV screening more consistent and traceable against job-specific criteria.
2. Help HR review relevant evidence and missing or unverified information.
3. Keep final recruitment decisions under authorized human control.
4. Handle processing and email failures without corrupting application decisions.
5. Protect candidate personal data and confidential recruitment information.
6. Maintain a history of important decisions and status changes.
7. Make the workflow testable, observable, and recoverable after failures.

## 3. Stakeholders and Roles

### 3.1 Candidate
- Submit an application and CV for an available job.
- Provide the required contact details.
- View the permitted status of their own application.
- Must not access other candidates' applications, CVs, reports, or private data.

### 3.2 HR User
- Create and manage authorized job openings.
- Configure job requirements, including minimum experience and whether that requirement is strict or flexible.
- Review AI evaluation reports and processing issues.
- Make application decisions, including shortlist, reject, or request further review.
- Select shortlisted candidates to receive interview invitations.
- Access only jobs and applications for which they are authorized.

### 3.3 Administrator
- Manage authorized system configuration and user/role administration.
- Access sensitive recruitment records only where explicitly authorized by the system's permission model.

### 3.4 System / AI Workflow
- Validate and process uploaded CVs.
- Extract information and evaluate evidence against configured job requirements.
- Produce a structured report and recommendation.
- Never make the final hiring decision autonomously.

---

## 4. Scope

### 4.1 In Scope
- Authentication and role-based access control (RBAC).
- Resource-level authorization and ownership checks.
- Job creation and management.
- Job-specific requirements and requirement strictness configuration.
- Candidate application submission and CV upload validation.
- CV text/data extraction and processing error handling.
- Evidence-based AI evaluation with structured output.
- Matching score and recommendation, with explanations and supporting evidence.
- Application statuses and candidate-facing status tracking.
- HR review and human approval/decision steps.
- Shortlist and rejection decisions.
- HR-controlled selection of candidates to invite to interviews.
- Candidate email notifications.
- Separate tracking of application status and email-delivery status.
- Retry handling, error logging, safe workflow recovery, and duplicate-action protection.
- Audit logging of important actions.
- Privacy, secure file handling, and data-retention rules.
- Testing, evaluation, and observability of AI-assisted screening.

### 4.2 Out of Scope
- AI-conducted online interviews, voice/video interviews, or interview automation.
- Speech-to-text or text-to-speech interview features.
- Automatic generation of interview questions as part of an AI interview.
- Interview transcript analysis.
- Personality, honesty, emotion, or suitability predictions from a candidate's face, voice, or video.
- AI making the final hiring or rejection decision without HR.
- Automatic rejection solely because CV parsing or processing failed.
- Unapproved automated posting or messaging on third-party job platforms.
- Any use of protected or sensitive personal attributes as a proxy for job suitability.

---

## 5. Functional Requirements

### FR-01 — Authentication
The system shall require users to authenticate before accessing protected candidate, HR, or administrative features.

### FR-02 — Role-Based Access Control
The system shall enforce permissions according to the user's role, such as Candidate, HR User, and Administrator.

### FR-03 — Resource-Level Authorization
The backend shall verify that the authenticated user is authorized to access the requested job, application, CV, report, or action. Candidate users shall only access their own applications. HR users shall only access the jobs and applications assigned or otherwise explicitly authorized to them.

### FR-04 — Job Management
Authorized HR users shall be able to create, view, update, and manage job openings.

### FR-05 — Job Requirement Configuration
For each job, authorized HR users shall be able to configure relevant skills, education criteria where applicable, minimum relevant experience, and whether the minimum-experience rule is `Strict` or `Flexible`.

### FR-06 — Candidate Application Submission
Candidates shall be able to submit an application with required contact information and a CV for a job that is accepting applications.

### FR-07 — CV Upload Validation
The system shall validate uploaded files against the supported file types, configured file-size limit, and basic file-safety checks before processing. Exact supported types and size limits remain open decisions.

### FR-08 — CV Processing and Information Extraction
The system shall attempt to extract relevant text and information from a valid uploaded CV. It shall preserve the application record if CV processing fails.

### FR-09 — Structured AI Evaluation
The system shall evaluate extracted CV evidence against the job's configured requirements and produce a structured report. The report shall distinguish confirmed evidence, confirmed mismatch where supportable, and information that is not found or cannot be verified.

### FR-10 — Evidence and Explanation
The evaluation report shall include supporting CV evidence for important claims where possible, matched requirements, missing or unverified requirements, experience comparison, and relevant limitations. The system shall not present an unsupported AI-generated claim as a verified fact.

### FR-11 — Matching Score and Recommendation
The system may provide a matching score and a recommendation such as `Recommended`, `Not Recommended`, or `Needs Review`. The score methodology must be documented and evaluated. A score alone shall not trigger an automatic final hiring decision.

### FR-12 — Strict and Flexible Experience Rules
The system shall apply the job's configured experience rule:
- If `Strict`, a confirmed shortfall shall block the normal shortlisting path and be clearly flagged.
- If `Flexible`, a shortfall shall be reported for HR consideration and shall not by itself cause automatic rejection.

Any exception to a strict requirement, if allowed at all, must be separately designed, explicitly authorized, and auditable. No exception workflow is assumed in this draft.

### FR-13 — Application Status Management
The system shall maintain an application status representing the application's workflow stage. Status changes shall follow defined transition rules. The complete transition table will be finalized during system design.

### FR-14 — Candidate Status Tracking
Candidates shall be able to view permitted, candidate-facing status information for their own applications. They shall not automatically receive access to internal AI reports, confidential HR notes, other candidates' data, or internal-only diagnostics.

### FR-15 — HR Review and Decision
Authorized HR users shall be able to review an evaluation report and make the final application decision. Available actions shall include the agreed decision paths, such as shortlist, reject, or send for further review. The exact transition rules will be finalized before implementation.

### FR-16 — Interview Invitation Selection
After shortlisting, authorized HR users shall select which candidates should receive interview invitations. The platform sends invitations; the actual interview is conducted by HR and is outside AI-interview scope.

### FR-17 — Candidate Email Notifications
The system shall support relevant candidate notifications, including shortlist, rejection, and interview invitation emails, according to the configured workflow and HR decisions.

### FR-18 — Separate Email Delivery State
The system shall store email-delivery state separately from application status. Email failure shall not reverse or delay a saved HR decision. Failed messages shall be logged and retried according to a defined policy, with protection against unintended duplicate sends.

### FR-19 — Retry and Error Handling
The system shall handle transient processing failures using a defined retry policy. CV processing shall allow at most three attempts in total: one initial attempt and two retries. If processing still fails, the application shall be marked `Needs Review`, the failure shall be logged, and the case shall be made visible to HR. Processing failure alone shall not cause automatic rejection.

### FR-20 — Workflow Recovery
If an application record has been created but workflow startup or execution fails, the system shall preserve the application record, log the failure, and provide a safe recovery or retry path. Recovery shall prevent duplicate application records and unintended duplicate side effects.

### FR-21 — Human-in-the-Loop Workflow
Where HR review or approval is required, the workflow shall pause until an authorized HR action is recorded. Workflow state shall be persisted so that the process can resume from the appropriate point. The system shall record the relevant HR action and verify authorization before resuming.

### FR-22 — Audit Logging
The system shall record important actions such as application status changes, HR decisions, authorization-relevant administrative actions, and workflow failures. Audit records should include the actor, action, affected record, timestamp, and relevant before/after state or reason where appropriate. Logs shall not unnecessarily copy CV text, credentials, API keys, or excessive personal data.

### FR-23 — Privacy and Data Minimization
The system shall process only personal information necessary for the recruitment workflow. Data sent to an AI provider shall be limited to what is needed for the task, subject to the selected provider and deployment design. Access to CVs, extracted content, reports, and logs shall be restricted. Data retention and deletion rules must be defined before production use.

### FR-24 — Evaluation and Observability
The development and test process shall evaluate AI output quality, evidence support, false matches, missed matches, and recommendation consistency. Workflow tracing and error observability shall be available to developers or authorized operators without unnecessarily exposing candidate personal data.

---

## 6. Non-Functional Requirements

### NFR-01 — Security
The system shall enforce authentication, backend authorization, secure file handling, least-privilege access, and protection of secrets. Sensitive data shall not be exposed through error messages or ordinary application logs.

### NFR-02 — Privacy
Candidate personal data shall be collected and processed only for defined recruitment purposes. Data retention, deletion, AI-provider handling, and access policies must be documented.

### NFR-03 — Reliability
A transient email or workflow failure shall not silently corrupt an application decision. Failures shall be logged and recoverable where feasible.

### NFR-04 — Data Integrity
Application decisions, status transitions, email-delivery records, and audit records shall be persisted consistently. Duplicate submissions and duplicate side effects shall be controlled.

### NFR-05 — Explainability
AI-assisted evaluations shall provide evidence and limitations sufficient to support HR review. A numeric score shall not be treated as a guaranteed probability of hiring or job performance.

### NFR-06 — Human Oversight
The system shall preserve authorized HR control over final shortlist/rejection decisions and interview invitations.

### NFR-07 — Maintainability
The application API, workflow orchestration, CV extraction, AI evaluation, persistence, email delivery, and frontend responsibilities should be separated so components can be tested and maintained independently.

### NFR-08 — Testability
Business rules, authorization checks, status transitions, retries, workflow recovery, email failures, and AI evaluation quality shall be testable using unit, integration, and workflow-level tests.

### NFR-09 — Performance
CV processing and user-facing response-time targets must be set after the expected workload, file-size limits, and deployment environment are decided. Long-running work should not unnecessarily block interactive API requests.

### NFR-10 — Accessibility and Usability
Candidate and HR interfaces should present statuses, errors, evaluation evidence, and required actions clearly. Important decisions shall not rely on a score or color alone.

### NFR-11 — Auditability
Important decision and workflow events shall be traceable. Audit records shall have restricted access and appropriate protection against unauthorized modification.

### NFR-12 — Fairness and Appropriate Use
Evaluation criteria shall be job-related and consistently applied. The system shall not infer personality, honesty, emotion, or general worth from protected/sensitive attributes or face/voice/video. AI evaluation quality and potential disparate errors should be assessed as part of testing.

---

## 7. Business Rules

### BR-01 — Human Final Decision
AI may assist with screening and recommendations, but authorized HR users make final shortlist/rejection decisions.

### BR-02 — Strict Experience Requirement
If a job's minimum experience is marked `Strict`, a confirmed shortfall blocks the normal shortlisting path. The system flags the shortfall for HR visibility.

### BR-03 — Flexible Experience Requirement
If a job's minimum experience is marked `Flexible`, a shortfall is reported for HR consideration and does not by itself cause automatic rejection.

### BR-04 — Job-Specific Configuration
The authorized HR user configures the experience threshold and strict/flexible behavior separately for each job.

### BR-05 — Missing Evidence Is Not Proof of Absence
If a skill or qualification is not mentioned in the CV, the system shall mark it `Evidence Not Found` or `Unverified`, rather than automatically asserting that the candidate does not have it.

### BR-06 — Unsupported AI Claims
A claim generated by AI must not be treated as verified unless supported by available evidence or independently confirmed. Material unsupported claims shall be flagged and may route the application to `Needs Review`.

### BR-07 — Processing Failure Is Not Rejection
If CV processing fails after the initial attempt and two retries, the system shall route the application to `Needs Review`, preserve the application record, and log the error.

### BR-08 — Email Failure Does Not Change the Decision
Email delivery failure shall not reverse or alter an already saved application decision. Email delivery state is tracked independently.

### BR-09 — Duplicate Side-Effect Protection
Workflow recovery and email retry logic shall avoid creating duplicate applications, duplicate decisions, or unintended duplicate emails.

### BR-10 — Candidate Data Ownership
A candidate may access only their own applications and permitted candidate-facing information.

### BR-11 — HR Resource Authorization
An HR user may access only the jobs, applications, CVs, and reports for which that user has explicit authorization.

### BR-12 — Audit Trail
Important status changes and HR decisions shall be auditable with actor and timestamp information and relevant context.

### BR-13 — Evidence-Based Evaluation
Matching scores and recommendations must be grounded in the configured job criteria and available CV evidence. The score alone shall not guarantee shortlisting or rejection.

### BR-14 — Data Minimization
Only information needed for the defined recruitment task shall be processed or sent to an AI provider. Sensitive data shall not be copied into logs without a justified need.

### BR-15 — Candidate Status Visibility
Candidates may see permitted status updates for their own applications but shall not automatically see internal HR notes or confidential internal evaluation details.

### BR-16 — Interview Process
The platform may send interview invitations only after an authorized HR user selects the shortlisted candidate for an invitation. The actual interview is conducted by HR, not AI.

---

## 8. Initial Application Statuses

The following are proposed workflow statuses. Their transition rules and exact candidate-facing wording must be finalized during system design.

- `Applied`
- `Processing`
- `Needs Review`
- `Screening Completed`
- `HR Review`
- `Shortlisted`
- `Rejected`
- `Interview Invited`

`Needs Review` is not equivalent to rejection. It indicates that human review or resolution is required.

Email-delivery state is separate from application status. Example email states may include `Pending`, `Sent`, `Failed`, and `Retry Scheduled`; exact values and transitions remain to be designed.

---

## 9. AI Evaluation Requirements

The AI evaluation report should, where applicable, contain:

1. Job and application identifiers.
2. Extracted relevant candidate information, with source/evidence references where feasible.
3. Requirement-by-requirement assessment.
4. Supporting evidence for claimed skills and experience.
5. Distinction between `Evidence Found`, `Evidence Not Found`, `Unverified`, and `Confirmed Mismatch` where the evidence supports that distinction.
6. Experience comparison against the configured threshold and strict/flexible rule.
7. Missing requirements and uncertainty.
8. Matching score, with a documented scoring methodology.
9. Recommendation: `Recommended`, `Not Recommended`, or `Needs Review`.
10. Warnings, limitations, or unsupported claims that require attention.

The system must not invent candidate qualifications. It must not assume that an omitted skill is absent. The score and recommendation are decision-support outputs, not the final hiring decision.

---

## 10. Error Handling and Recovery

### 10.1 CV Processing Failure
- Preserve the application record.
- Attempt processing up to three times in total.
- If all attempts fail, set the application to `Needs Review`.
- Record a useful error category and relevant diagnostic information without unnecessarily logging CV contents or secrets.
- Make the case visible to authorized HR users.

### 10.2 Workflow Startup Failure
- Preserve the created application.
- Record workflow-start failure.
- Allow safe recovery/retry.
- Prevent duplicate workflow execution or duplicate application creation.

### 10.3 Server Restart During Workflow
- Persist workflow state/checkpoints for workflows that need to pause and resume.
- Use stable workflow/application identifiers and appropriate checkpoint configuration.
- Implement recovery logic; a persisted checkpoint alone does not guarantee that every interrupted job will automatically resume.
- Ensure resumed work does not repeat non-idempotent side effects, such as sending an email or saving the same decision twice.

### 10.4 Email Failure
- Keep the saved application decision unchanged.
- Store delivery state separately.
- Log the failure and retry according to a defined policy.
- Use duplicate-send protection and track attempts.

### 10.5 HR Review Pause
- Pause the workflow when human action is required.
- Persist state.
- Verify the acting HR user's authorization.
- Record the action and resume the appropriate workflow branch.

---

## 11. Human-in-the-Loop (HITL)

The workflow shall involve authorized HR users at the decision points that require human judgment.

Minimum behavior:
1. AI prepares a report and recommendation.
2. The workflow persists the report and pauses for HR review where required.
3. The HR user reviews the evidence and limitations.
4. The backend verifies that the user is authorized for that application.
5. The HR decision and relevant audit details are persisted.
6. The workflow resumes along the appropriate branch.
7. Any notification is initiated without allowing an email failure to reverse the HR decision.

---

## 12. Acceptance Criteria

### AC-01 — Application Submission
**Given** a candidate submits valid required details and a supported CV, **when** the application is accepted, **then** the system creates one application record and begins the defined processing workflow.

### AC-02 — CV Processing Failure
**Given** CV processing fails, **when** the initial attempt and two retries have all failed, **then** the application remains stored, its status becomes `Needs Review`, the failure is logged, and the case is available to authorized HR. It is not automatically rejected.

### AC-03 — Strict Experience Validation
**Given** a job has a strict minimum-experience rule, **when** reliable evidence shows the candidate is below that threshold, **then** the system flags the shortfall and blocks the normal shortlisting path.

### AC-04 — Flexible Experience Validation
**Given** a job has a flexible minimum-experience rule, **when** the candidate is below that threshold, **then** the system reports the shortfall for HR review and does not automatically reject the candidate for that reason alone.

### AC-05 — Missing Skill Evidence
**Given** a skill is not mentioned in the CV, **when** the system evaluates that requirement, **then** it marks the evidence as not found or unverified rather than asserting that the candidate definitely lacks the skill.

### AC-06 — HR Decision and Email Failure
**Given** an authorized HR user saves a shortlist or rejection decision, **when** the notification email fails, **then** the application decision remains unchanged, the email failure is recorded separately, and the message may be retried according to policy.

### AC-07 — Candidate Authorization
**Given** Candidate A is authenticated, **when** they attempt to access Candidate B's application or CV, **then** the backend denies access and does not reveal the protected record.

### AC-08 — HR Resource Authorization
**Given** an HR user is not authorized for a particular job/application, **when** they attempt to access its CV or report, **then** the backend denies access unless explicit permission is granted.

### AC-09 — Audit Logging
**Given** an important application status or HR decision changes, **when** the change is committed, **then** an audit record captures the actor, action, timestamp, affected record, and relevant context without unnecessarily copying sensitive personal data.

### AC-10 — Candidate Status Visibility
**Given** a candidate is authenticated, **when** they view their application, **then** they see only permitted status information for their own application and do not receive internal HR notes or other candidates' data.

### AC-11 — Evidence-Based AI Report
**Given** an AI report contains a material claim unsupported by the CV evidence, **when** the system validates the report, **then** the claim is not presented as verified and is flagged for correction or review as appropriate.

### AC-12 — Workflow Recovery
**Given** a workflow fails after an application record has been created, **when** recovery is attempted, **then** the system preserves the existing record and avoids duplicate application creation and unintended duplicate side effects.

### AC-13 — HR-Controlled Interview Invitation
**Given** a candidate has been shortlisted, **when** no authorized HR user has selected them for an interview invitation, **then** the system does not send an interview invitation automatically.

### AC-14 — Data Minimization
**Given** CV information is sent to an AI service, **when** the request is prepared, **then** only information needed for the defined task is included, according to the approved provider and privacy design.

---

## 13. Open Decisions — Must Be Resolved Before Implementation

These items are intentionally open; they should not be silently assumed.

1. **Supported CV formats:** PDF only, or PDF and DOCX? Is scanned/image-only CV support required?
2. **Maximum upload size:** What file-size limit should apply?
3. **Storage:** Where will original CV files and extracted text be stored, and how will access be secured?
4. **Retention/deletion:** How long should applications, CVs, AI reports, email records, and audit logs be retained? What deletion process is required?
5. **AI provider:** Which model/provider will be used, and what are its data-use and retention settings?
6. **Scoring method:** What criteria and weights define the matching score? How will scores be calibrated and tested?
7. **Education rules:** Which education requirements can be configured, and are any strict or flexible?
8. **Status transitions:** Which transitions are permitted, and can HR reopen or correct a decision?
9. **Candidate-facing statuses:** Should `Needs Review` be shown directly, or mapped to a less technical phrase such as `Under Review`?
10. **Email policy:** Which provider will be used, how many retries, what retry intervals, and when does a message become permanently failed?
11. **Duplicate protection:** What idempotency keys or unique constraints will be used for submissions, workflow starts, and email sends?
12. **Authentication:** Which sign-in method and password/session policies will be used?
13. **HR permissions:** Are applications assigned by job, department, team, or explicit permissions? Who can grant access?
14. **Performance targets:** What expected number of concurrent users and applications per day should be supported? What are acceptable processing and API response times?
15. **Failure notifications:** How should HR be notified when workflow or CV processing needs intervention?
16. **Accessibility and language:** Which interface languages are required, and what accessibility standard is targeted?
17. **Legal/compliance review:** Which jurisdiction and organizational privacy/recruitment policies apply?
18. **AI evaluation:** What test dataset, quality metrics, error thresholds, and review procedure will be used?
19. **Audit protection:** Which roles can read audit logs, and what protections against alteration are required?
20. **Strict-rule exceptions:** Should exceptions to strict experience requirements be prohibited entirely, or should an explicitly authorized and audited exception path exist?

---

## 14. Agreed Architecture Direction (High-Level Only)

This section records boundaries, not a final architecture or technology commitment.

- **Frontend:** Candidate application/status interface and HR dashboard.
- **FastAPI backend:** API endpoints, input validation, authentication/authorization, persistence coordination, and workflow initiation.
- **PostgreSQL:** Persistent records for users, jobs, applications, decisions, evaluation metadata, email-delivery state, and audit events.
- **CV processing components:** Extract text/data from supported CV formats.
- **AI evaluation layer:** Evaluate extracted evidence against job-specific criteria and return validated structured results.
- **LangGraph (planned):** Orchestrate workflow steps, conditional paths, retries, and human review pause/resume where appropriate.
- **Email service:** Send notifications and report delivery state independently from application status.
- **Secure file storage (decision pending):** Store original CV files and restrict access.
- **Evaluation/observability tools (to be selected):** Test AI quality and trace workflow behavior while minimizing exposure of personal data.

The implementation should keep API coordination, workflow orchestration, AI evaluation, persistence, file storage, and email delivery as distinct responsibilities. RAG/vector search should only be added if a demonstrated requirement benefits from it; it is not assumed to be necessary for every CV-screening operation.

---

## 15. Document Change Log

- **v1.0:** Initial requirements draft.
- **v2.0:** Consolidated agreed decisions: configurable strict/flexible experience rules, evidence-based AI evaluation, candidate status tracking, email/application state separation, resource-level authorization, audit logging, privacy/data minimization, explicit acceptance criteria, and expanded open decisions.
