import json
import logging
from typing import Any

from app.models import SessionLocal
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def log_audit_event(action: str, entity_type: str | None = None, entity_id: Any | None = None,
                    actor: str | None = None, details: dict | None = None) -> None:
    db = SessionLocal()
    try:
        payload = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            actor=actor,
            details=json.dumps(details or {}),
        )
        db.add(payload)
        db.commit()
    except Exception as exc:
        logger.warning("Failed to persist audit event %s: %s", action, exc)
        db.rollback()
    finally:
        db.close()
