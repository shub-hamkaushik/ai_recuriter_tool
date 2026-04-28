from flask import Blueprint, request, jsonify
from app.models import get_db
from app.models.candidate import Candidate
from app.models.job import JobDescription
from app.models.match_result import MatchResult
from app.services.audit_service import log_audit_event
from app.services.matching_service import match_candidate_to_jobs, match_job_to_candidates
from app.services.ai_service import generate_summary_and_fit
from app.services.auth_service import roles_required

bp = Blueprint('matching', __name__)


def serialize_match_result(result: MatchResult) -> dict:
    return {
        'id': result.id,
        'candidate_id': result.candidate_id,
        'job_id': result.job_id,
        'skill_match_score': result.skill_match_score,
        'experience_match_score': result.experience_match_score,
        'overall_score': result.overall_score,
        'fit_explanation': result.fit_explanation,
        'hiring_recommendation': result.hiring_recommendation,
    }

@bp.route('/candidate/<int:candidate_id>', methods=['POST'])
@roles_required("admin", "hr")
def match_candidate_to_all_jobs(candidate_id, current_user):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return jsonify({'error': 'Candidate not found'}), 404
        
        jobs = db.query(JobDescription).filter((JobDescription.status == None) | (JobDescription.status == "Open")).all()
        matches = match_candidate_to_jobs(candidate, jobs)
        
        # Store results
        for match in matches:
            existing = db.query(MatchResult).filter(
                MatchResult.candidate_id == candidate_id,
                MatchResult.job_id == match["job_id"],
            ).first()
            if existing:
                existing.skill_match_score = match["skill_match_score"]
                existing.experience_match_score = match["experience_match_score"]
                existing.overall_score = match["overall_score"]
                continue
            db_match = MatchResult(
                candidate_id=candidate_id,
                job_id=match["job_id"],
                skill_match_score=match["skill_match_score"],
                experience_match_score=match["experience_match_score"],
                overall_score=match["overall_score"]
            )
            db.add(db_match)
        db.commit()
        log_audit_event("candidate_matching_run", "candidate", candidate_id, current_user.username, {"job_count": len(matches)})
        
        return jsonify(matches), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/job/<int:job_id>', methods=['GET'])
@roles_required("admin", "hr")
def get_ranked_candidates_for_job(job_id, current_user):
    db = next(get_db())
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        candidates = db.query(Candidate).all()
        matches = match_job_to_candidates(job, candidates)

        return jsonify(matches), 200
    finally:
        db.close()

@bp.route('/job/<int:job_id>', methods=['POST'])
@roles_required("admin", "hr")
def match_job_to_all_candidates(job_id, current_user):
    db = next(get_db())
    try:
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        candidates = db.query(Candidate).all()
        matches = match_job_to_candidates(job, candidates)

        # Store results
        for match in matches:
            existing = db.query(MatchResult).filter(
                MatchResult.candidate_id == match["candidate_id"],
                MatchResult.job_id == job_id,
            ).first()
            if existing:
                existing.skill_match_score = match["skill_match_score"]
                existing.experience_match_score = match["experience_match_score"]
                existing.overall_score = match["overall_score"]
                continue
            db_match = MatchResult(
                candidate_id=match["candidate_id"],
                job_id=job_id,
                skill_match_score=match["skill_match_score"],
                experience_match_score=match["experience_match_score"],
                overall_score=match["overall_score"]
            )
            db.add(db_match)
        db.commit()
        log_audit_event("job_matching_run", "job", job_id, current_user.username, {"candidate_count": len(matches)})
        
        return jsonify(matches), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@bp.route('/results', methods=['GET'])
@roles_required("admin", "hr")
def get_match_results(current_user):
    db = next(get_db())
    try:
        candidate_id = request.args.get('candidate_id', type=int)
        job_id = request.args.get('job_id', type=int)
        
        query = db.query(MatchResult)
        if candidate_id:
            query = query.filter(MatchResult.candidate_id == candidate_id)
        if job_id:
            query = query.filter(MatchResult.job_id == job_id)
        
        results = query.all()
        result_list = [serialize_match_result(r) for r in results]
        
        return jsonify(result_list), 200
    finally:
        db.close()

@bp.route('/ai-summary/<int:candidate_id>/<int:job_id>', methods=['POST'])
@roles_required("admin", "hr")
def generate_ai_summary(candidate_id, job_id, current_user):
    db = next(get_db())
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
        if not candidate or not job:
            return jsonify({'error': 'Candidate or Job not found'}), 404
        
        candidate_data = {
            "name": candidate.name,
            "skills": candidate.parsed_skills,
            "experience": candidate.experience_years
        }
        job_data = {
            "title": job.title,
            "required_skills": job.required_skills,
            "min_experience": job.minimum_experience
        }
        
        result = generate_summary_and_fit(candidate_data, job_data)
        candidate.ai_summary = result.get("summary", candidate.ai_summary)
        match_record = db.query(MatchResult).filter(
            MatchResult.candidate_id == candidate_id,
            MatchResult.job_id == job_id,
        ).first()
        if match_record:
            match_record.fit_explanation = result.get("fit_explanation")
            match_record.hiring_recommendation = result.get("hiring_recommendation")
        db.commit()
        log_audit_event("fit_explanation_generated", "match_result", f"{candidate_id}:{job_id}", current_user.username)
        return jsonify(result), 200
    finally:
        db.close()
