from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    actor_id: int | None = None,
    application_id: int | None = None,
    details: dict | None = None
):
    """
    Create an audit log entry.

    This function only adds the log to the current transaction.
    The caller controls when the transaction is committed.
    """

    audit_log = AuditLog(
        actor_id=actor_id,
        application_id=application_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )

    db.add(audit_log)

    return audit_log