from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from uuid import uuid4
from pathlib import Path
from app.models import get_db
from app.models.candidate import Candidate
from app.config import settings
from app.services.audit_service import log_audit_event
from app.services.ai_service import parse_resume_with_llm
from app.services.auth_service import roles_required

bp = Blueprint('candidates', __name__)

UPLOAD_DIR = Path(settings.upload_dir)
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_resume_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    if extension == ".txt":
        return file_path.read_text(encoding="utf-8")
    if extension == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("PDF uploads require pypdf to extract raw text") from exc
        reader = PdfReader(str(file_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        if not text:
            raise ValueError("No extractable text found in PDF resume")
        return text
    raise ValueError("Unsupported file type")


def serialize_candidate(candidate: Candidate, include_resume_text: bool = False) -> dict:
    payload = {
        'id': candidate.id,
        'name': candidate.name,
        'email': candidate.email,
        'experience_years': candidate.experience_years,
        'parsed_skills': candidate.parsed_skills or [],
        'status': candidate.status or "New",
        'education_details': candidate.education_details,
        'work_history_summary': candidate.work_history_summary,
        'ai_summary': candidate.ai_summary,
        'resume_filename': candidate.resume_filename,
        'created_at': candidate.created_at.isoformat() if candidate.created_at else None,
    }
    if include_resume_text:
        payload['raw_resume_text'] = candidate.raw_resume_text
    return payload


@bp.route('/', methods=['POST'])
@roles_required("admin", "hr")
def create_candidate(current_user):
    db = next(get_db())
    try:
        data = request.get_json() or {}
        required = ["name", "email"]
        missing = [field for field in required if not data.get(field)]
        if missing:
            return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

        if db.query(Candidate).filter(Candidate.email == data["email"]).first():
            return jsonify({'error': 'Candidate with this email already exists'}), 400

        candidate = Candidate(
            name=data["name"],
            email=data["email"],
            experience_years=data.get("experience_years", 0),
            parsed_skills=data.get("parsed_skills", []),
            raw_resume_text=data.get("raw_resume_text"),
            status=data.get("status", "New"),
            education_details=data.get("education_details"),
            work_history_summary=data.get("work_history_summary"),
            ai_summary=data.get("ai_summary"),
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        log_audit_event("candidate_created", "candidate", candidate.id, current_user.username, {"email": candidate.email})
        return jsonify(serialize_candidate(candidate, include_resume_text=True)), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/upload', methods=['POST'])
@roles_required("admin", "hr")
def upload_resume(current_user):
    db = next(get_db())
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        file = request.files.get('file')
        
        if not name or not email or not file:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Check if candidate exists
        db_candidate = db.query(Candidate).filter(Candidate.email == email).first()
        if db_candidate:
            return jsonify({'error': 'Candidate with this email already exists'}), 400
        
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        original_filename = secure_filename(file.filename)
        suffix = Path(original_filename).suffix.lower()
        filename = f"{uuid4().hex}{suffix}"
        file_path = UPLOAD_DIR / filename
        file.save(file_path)
        
        raw_text = extract_resume_text(file_path)
        
        # Parse with LLM
        parsed_data = parse_resume_with_llm(raw_text)
        
        # Create candidate
        candidate = Candidate(
            name=name,
            email=email,
            experience_years=parsed_data.get("experience_years", 0),
            parsed_skills=parsed_data.get("skills", []),
            raw_resume_text=raw_text,
            resume_filename=filename,
            status="New",
            education_details=parsed_data.get("education"),
            work_history_summary=parsed_data.get("work_history_summary"),
            ai_summary=parsed_data.get("professional_summary"),
        )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        log_audit_event("resume_uploaded", "candidate", candidate.id, current_user.username, {"filename": filename})

        return jsonify(serialize_candidate(candidate)), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/', methods=['GET'])
@roles_required("admin", "hr")
def get_candidates(current_user):
    db = next(get_db())
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 10))
        
        query = db.query(Candidate)
        total = query.count()
        candidates = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
        result = [serialize_candidate(c) for c in candidates]
        
        return jsonify({"items": result, "total": total, "skip": skip, "limit": limit}), 200
    finally:
        db.close()

@bp.route('/<int:candidate_id>', methods=['GET'])
@roles_required("admin", "hr")
def get_candidate(candidate_id, current_user):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        return jsonify(serialize_candidate(candidate, include_resume_text=True)), 200
    finally:
        db.close()


@bp.route('/<int:candidate_id>', methods=['PUT'])
@roles_required("admin", "hr")
def update_candidate(candidate_id, current_user):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404

        data = request.get_json() or {}
        allowed_fields = {
            "name", "email", "experience_years", "parsed_skills", "raw_resume_text",
            "status", "education_details", "work_history_summary", "ai_summary"
        }
        for key, value in data.items():
            if key in allowed_fields:
                setattr(candidate, key, value)

        db.commit()
        db.refresh(candidate)
        log_audit_event("candidate_updated", "candidate", candidate.id, current_user.username, {"fields": list(data.keys())})
        return jsonify(serialize_candidate(candidate, include_resume_text=True)), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:candidate_id>/reprocess', methods=['POST'])
@roles_required("admin", "hr")
def reprocess_candidate(candidate_id, current_user):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        if not candidate.raw_resume_text:
            return jsonify({'error': 'Candidate has no stored resume text'}), 400

        parsed_data = parse_resume_with_llm(candidate.raw_resume_text)
        candidate.experience_years = parsed_data.get("experience_years", candidate.experience_years)
        candidate.parsed_skills = parsed_data.get("skills", candidate.parsed_skills)
        candidate.education_details = parsed_data.get("education", candidate.education_details)
        candidate.work_history_summary = parsed_data.get("work_history_summary", candidate.work_history_summary)
        candidate.ai_summary = parsed_data.get("professional_summary", candidate.ai_summary)
        db.commit()
        db.refresh(candidate)
        log_audit_event("candidate_reprocessed", "candidate", candidate.id, current_user.username)
        return jsonify(serialize_candidate(candidate, include_resume_text=True)), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/<int:candidate_id>', methods=['DELETE'])
@roles_required("admin")
def delete_candidate(candidate_id, current_user):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        db.delete(candidate)
        db.commit()
        
        # Remove file
        if candidate.resume_filename:
            file_path = UPLOAD_DIR / candidate.resume_filename
            if file_path.exists():
                file_path.unlink()
        log_audit_event("candidate_deleted", "candidate", candidate.id, current_user.username, {"email": candidate.email})
        
        return jsonify({'message': 'Candidate deleted'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
