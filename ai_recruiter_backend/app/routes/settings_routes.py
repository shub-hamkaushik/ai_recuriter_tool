from flask import Blueprint, jsonify, request

from app.models import get_db
from app.models.audit_log import AuditLog
from app.models.system_setting import SystemSetting
from app.services.audit_service import log_audit_event
from app.services.auth_service import roles_required

bp = Blueprint("settings", __name__)

DEFAULT_SETTINGS = {
    "enableAiSummaries": "true",
    "enableFitExplanations": "true",
    "auditLogging": "true",
}


def _coerce(value: str):
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


@bp.route("/", methods=["GET"])
@roles_required("admin")
def get_settings(current_user):
    db = next(get_db())
    try:
        settings = {setting.key: _coerce(setting.value or "") for setting in db.query(SystemSetting).all()}
        for key, value in DEFAULT_SETTINGS.items():
            settings.setdefault(key, _coerce(value))
        return jsonify(settings), 200
    finally:
        db.close()


@bp.route("/", methods=["PUT"])
@roles_required("admin")
def update_settings(current_user):
    db = next(get_db())
    try:
        data = request.get_json() or {}
        for key, value in data.items():
            setting = db.query(SystemSetting).filter(SystemSetting.key == key).first()
            if not setting:
                setting = SystemSetting(key=key)
                db.add(setting)
            setting.value = str(value).lower() if isinstance(value, bool) else str(value)
        db.commit()
        log_audit_event("settings_updated", "system_settings", actor=current_user.username, details=data)
        return jsonify({"message": "Settings updated"}), 200
    finally:
        db.close()


@bp.route("/audit-logs", methods=["GET"])
@roles_required("admin")
def get_audit_logs(current_user):
    db = next(get_db())
    try:
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
        return jsonify([
            {
                "id": log.id,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "actor": log.actor,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]), 200
    finally:
        db.close()
