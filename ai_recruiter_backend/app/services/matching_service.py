from typing import Dict, List, Tuple
from app.models.candidate import Candidate
from app.models.job import JobDescription

def _normalize_skills(skills: List[str]) -> set[str]:
    return {skill.strip().lower() for skill in skills if isinstance(skill, str) and skill.strip()}

def calculate_skill_match(candidate_skills: List[str], required_skills: List[str]) -> Tuple[float, List[str]]:
    if not required_skills:
        return 100.0, []
    candidate_skill_set = _normalize_skills(candidate_skills or [])
    required_skill_set = _normalize_skills(required_skills or [])
    if not required_skill_set:
        return 100.0, []
    overlapping_skills = sorted(candidate_skill_set & required_skill_set)
    score = (len(overlapping_skills) / len(required_skill_set)) * 100
    return round(score, 2), overlapping_skills

def calculate_experience_match(candidate_experience: float, min_experience: float) -> float:
    return 100.0 if (candidate_experience or 0) >= (min_experience or 0) else 0.0

def calculate_overall_score(skill_score: float, experience_score: float, skill_weight: float = 0.7, experience_weight: float = 0.3) -> float:
    return round(skill_score * skill_weight + experience_score * experience_weight, 2)

def match_candidate_to_jobs(candidate: Candidate, jobs: List[JobDescription]) -> List[Dict]:
    results = []
    for job in jobs:
        skill_score, overlapping_skills = calculate_skill_match(candidate.parsed_skills or [], job.required_skills or [])
        exp_score = calculate_experience_match(candidate.experience_years or 0, job.minimum_experience or 0)
        overall = calculate_overall_score(skill_score, exp_score)
        results.append({
            "job_id": job.id,
            "job_title": job.title,
            "overlapping_skills": overlapping_skills,
            "skill_match_score": skill_score,
            "experience_match_score": exp_score,
            "overall_score": overall
        })
    return sorted(results, key=lambda x: x["overall_score"], reverse=True)

def match_job_to_candidates(job: JobDescription, candidates: List[Candidate]) -> List[Dict]:
    results = []
    for candidate in candidates:
        skill_score, overlapping_skills = calculate_skill_match(candidate.parsed_skills or [], job.required_skills or [])
        exp_score = calculate_experience_match(candidate.experience_years or 0, job.minimum_experience or 0)
        overall = calculate_overall_score(skill_score, exp_score)
        results.append({
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "candidate_email": candidate.email,
            "candidate_experience_years": candidate.experience_years,
            "overlapping_skills": overlapping_skills,
            "skill_match_score": skill_score,
            "experience_match_score": exp_score,
            "overall_score": overall
        })
    return sorted(results, key=lambda x: x["overall_score"], reverse=True)
