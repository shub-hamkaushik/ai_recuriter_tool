from flask import Blueprint, request, jsonify
from app.models import get_db
from app.models.job import JobDescription
from app.services.audit_service import log_audit_event
from app.services.ai_service import enhance_job_description
from app.services.auth_service import roles_required

bp = Blueprint('jobs', __name__)


def serialize_job(job: JobDescription) -> dict:
    return {
        'id': job.id,
        'title': job.title,
        'department': job.department,
        'required_skills': job.required_skills or [],
        'minimum_experience': job.minimum_experience,
        'description': job.description,
        'location': job.location,
        'employment_type': job.employment_type,
        'status': job.status or "Open",
        'enhanced_description': job.enhanced_description,
        'created_at': job.created_at.isoformat() if job.created_at else None,
    }

@bp.route('/', methods=['POST'])
@roles_required("admin", "hr")
def create_job(current_user):
    db = next(get_db())
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        allowed_fields = {
            "title", "department", "required_skills", "minimum_experience",
            "description", "location", "employment_type", "status", "enhanced_description"
        }
        job_data = {key: value for key, value in data.items() if key in allowed_fields}
        missing_fields = [field for field in ["title", "department", "description"] if not job_data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        job = JobDescription(**job_data)
        db.add(job)
        db.commit()
        db.refresh(job)
        log_audit_event("job_created", "job", job.id, current_user.username, {"title": job.title})

        return jsonify(serialize_job(job)), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/', methods=['GET'])
@roles_required("admin", "hr")
def get_jobs(current_user):
    db = next(get_db())
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 10))
        
        query = db.query(JobDescription)
        total = query.count()
        jobs = query.order_by(JobDescription.created_at.desc()).offset(skip).limit(limit).all()
        result = [serialize_job(j) for j in jobs]
        
        return jsonify({"items": result, "total": total, "skip": skip, "limit": limit}), 200
    finally:
        db.close()

@bp.route('/<int:job_id>', methods=['GET'])
@roles_required("admin", "hr")
def get_job(job_id, current_user):
    db = next(get_db())
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        return jsonify(serialize_job(job)), 200
    finally:
        db.close()

@bp.route('/<int:job_id>', methods=['PUT'])
@roles_required("admin", "hr")
def update_job(job_id, current_user):
    db = next(get_db())
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        allowed_fields = {
            "title", "department", "required_skills", "minimum_experience",
            "description", "location", "employment_type", "status", "enhanced_description"
        }
        for key, value in data.items():
            if key in allowed_fields:
                setattr(job, key, value)
        
        db.commit()
        db.refresh(job)
        log_audit_event("job_updated", "job", job.id, current_user.username, {"fields": list(data.keys())})
        
        return jsonify(serialize_job(job)), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:job_id>/enhance', methods=['POST'])
@roles_required("admin", "hr")
def enhance_job(job_id, current_user):
    db = next(get_db())
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        enhancement = enhance_job_description(serialize_job(job))
        job.enhanced_description = enhancement["enhanced_description"]
        db.commit()
        db.refresh(job)
        log_audit_event("job_enhanced", "job", job.id, current_user.username)
        return jsonify(serialize_job(job)), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/<int:job_id>', methods=['DELETE'])
@roles_required("admin")
def delete_job(job_id, current_user):
    db = next(get_db())
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        db.delete(job)
        db.commit()
        log_audit_event("job_deleted", "job", job.id, current_user.username, {"title": job.title})
        
        return jsonify({'message': 'Job deleted'}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()
