import bcrypt
from functools import wraps
from flask import jsonify
from sqlalchemy.orm import Session
from flask_jwt_extended import create_access_token, get_jwt_identity, verify_jwt_in_request
from app.models import SessionLocal
from app.models.user import User

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    if not user.is_active:
        return False
    return user

def create_access_token_for_user(user: User):
    return create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "username": user.username},
    )

def check_admin_role(user: User):
    if not user or user.role != "admin":
        from flask import abort
        abort(403, description="Not enough permissions")

def roles_required(*allowed_roles):
    """Require a valid JWT and, when provided, one of the listed user roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == int(user_id)).first()
                if not user or not user.is_active:
                    return jsonify({"error": "Invalid or inactive user"}), 401
                if allowed_roles and user.role not in allowed_roles:
                    return jsonify({"error": "Not enough permissions"}), 403
                return fn(*args, current_user=user, **kwargs)
            finally:
                db.close()
        return wrapper
    return decorator
