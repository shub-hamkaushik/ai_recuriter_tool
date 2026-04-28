from flask import Blueprint, jsonify
from app.models import get_db
from app.models.candidate import Candidate
from app.models.job import JobDescription
from app.models.match_result import MatchResult
from app.services.auth_service import roles_required

bp = Blueprint("dashboard", __name__)


@bp.route("/summary", methods=["GET"])
@roles_required("admin", "hr")
def get_dashboard_summary(current_user):
    db = next(get_db())
    try:
        candidates = db.query(Candidate).order_by(Candidate.created_at.desc()).all()
        jobs = db.query(JobDescription).order_by(JobDescription.created_at.desc()).all()
        matches = db.query(MatchResult).all()

        recent_resumes = [
            {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "created_at": candidate.created_at.isoformat() if candidate.created_at else None,
            }
            for candidate in candidates[:5]
        ]
        recent_jobs = [
            {
                "id": job.id,
                "title": job.title,
                "department": job.department,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            }
            for job in jobs[:5]
        ]

        return jsonify({
            "totalCandidates": len(candidates),
            "activeJobs": len([job for job in jobs if (job.status or "Open") == "Open"]),
            "resumesUploaded": len(candidates),
            "successfulMatches": len(matches),
            "recentResumes": recent_resumes,
            "recentJobs": recent_jobs,
        }), 200
    finally:
        db.close()
