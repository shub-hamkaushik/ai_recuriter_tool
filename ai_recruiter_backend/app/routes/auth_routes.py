from flask import Blueprint, request, jsonify
from app.models import get_db
from app.models.user import User
from app.services.audit_service import log_audit_event
from app.services.auth_service import authenticate_user, create_access_token_for_user, hash_password, roles_required

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
@roles_required("admin")
def register(current_user):
    db = next(get_db())
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'hr')
        
        if not username or not email or not password:
            return jsonify({'error': 'Missing required fields'}), 400
        if role not in {"admin", "hr"}:
            return jsonify({'error': 'Role must be admin or hr'}), 400
        
        db_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if db_user:
            return jsonify({'error': 'Username or email already registered'}), 400
        
        hashed_password = hash_password(password)
        new_user = User(username=username, email=email, hashed_password=hashed_password, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        log_audit_event("user_registered", "user", new_user.id, current_user.username, {"role": new_user.role})
        
        access_token = create_access_token_for_user(new_user)
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer',
            'user': {'id': new_user.id, 'username': new_user.username, 'role': new_user.role}
        }), 201
    finally:
        db.close()

@bp.route('/login', methods=['POST'])
def login():
    db = next(get_db())
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Missing username or password'}), 400
        
        user = authenticate_user(db, username, password)
        if not user:
            log_audit_event("login_failed", "user", actor=username)
            return jsonify({'error': 'Incorrect username or password'}), 401
        log_audit_event("login_succeeded", "user", user.id, user.username, {"role": user.role})
        access_token = create_access_token_for_user(user)
        return jsonify({
            'access_token': access_token,
            'token_type': 'bearer',
            'user': {'id': user.id, 'username': user.username, 'role': user.role}
        }), 200
    finally:
        db.close()


@bp.route('/users', methods=['GET'])
@roles_required("admin")
def list_users(current_user):
    db = next(get_db())
    try:
        users = db.query(User).all()
        return jsonify([
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
            }
            for user in users
        ]), 200
    finally:
        db.close()


@bp.route('/users/<int:user_id>', methods=['PUT'])
@roles_required("admin")
def update_user(user_id, current_user):
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json() or {}
        if "role" in data and data["role"] in {"admin", "hr"}:
            user.role = data["role"]
        if "is_active" in data:
            user.is_active = bool(data["is_active"])
        db.commit()
        db.refresh(user)
        log_audit_event("user_updated", "user", user.id, current_user.username, {"role": user.role, "is_active": user.is_active})
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
        }), 200
    finally:
        db.close()
