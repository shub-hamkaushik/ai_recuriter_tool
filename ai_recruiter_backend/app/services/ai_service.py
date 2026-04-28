import json
import logging
import re
from typing import Any, Dict, Optional

import httpx

from app.config import settings
from app.services.audit_service import log_audit_event

logger = logging.getLogger(__name__)

KNOWN_SKILLS = {
    "python", "flask", "django", "fastapi", "sql", "postgresql", "mysql",
    "sqlalchemy", "rest", "api", "docker", "kubernetes", "aws", "azure",
    "javascript", "typescript", "angular", "react", "node", "java",
    "spring", "machine learning", "nlp", "pandas", "numpy",
}


def _heuristic_resume_parse(resume_text: str) -> Dict[str, Any]:
    normalized_text = resume_text.lower()
    skills = sorted(
        skill.title() if len(skill) > 3 else skill.upper()
        for skill in KNOWN_SKILLS
        if skill in normalized_text
    )
    experience_years = 0.0
    match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", normalized_text)
    if match:
        experience_years = float(match.group(1))
    education_match = re.search(
        r"(bachelor(?:'s)?|master(?:'s)?|b\.tech|m\.tech|mba|phd|computer science|engineering)",
        normalized_text,
    )
    work_summary = ""
    work_match = re.search(r"((?:worked|experience|developer|engineer).{0,240})", resume_text, re.IGNORECASE | re.DOTALL)
    if work_match:
        work_summary = " ".join(work_match.group(1).split())
    summary_parts = []
    if skills:
        summary_parts.append(f"Skilled in {', '.join(skills[:5])}.")
    if experience_years:
        summary_parts.append(f"Brings approximately {experience_years:.1f} years of experience.")
    if work_summary:
        summary_parts.append(work_summary)
    return {
        "skills": skills,
        "experience_years": experience_years,
        "education": education_match.group(0).title() if education_match else "Not provided",
        "work_history_summary": work_summary or "Work history not extracted.",
        "professional_summary": " ".join(summary_parts) or "Candidate summary unavailable.",
    }


def _local_enhanced_job_description(job_data: Dict[str, Any]) -> Dict[str, str]:
    original = (job_data.get("description") or "").strip()
    improved = original
    if job_data.get("location"):
        improved += f"\n\nLocation: {job_data['location']}"
    if job_data.get("employment_type"):
        improved += f"\nEmployment Type: {job_data['employment_type']}"
    if job_data.get("required_skills"):
        improved += f"\nKey Skills: {', '.join(job_data['required_skills'])}"
    return {
        "enhanced_description": improved or "No description provided.",
    }


def _local_summary_and_fit(candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, str]:
    candidate_skills = candidate_data.get("skills") or []
    required_skills = job_data.get("required_skills") or []
    overlapping = sorted({skill.lower() for skill in candidate_skills} & {skill.lower() for skill in required_skills})
    summary = candidate_data.get("professional_summary") or (
        f"{candidate_data.get('name', 'Candidate')} has experience with {', '.join(candidate_skills[:5]) or 'relevant technologies'}."
    )
    fit_explanation = (
        f"Matches on {', '.join(overlapping) if overlapping else 'limited overlapping skills'} "
        f"for the {job_data.get('title', 'role')} position."
    )
    recommendation = "Strong shortlist" if len(overlapping) >= max(1, len(required_skills) // 2) else "Needs further review"
    return {
        "summary": summary,
        "fit_explanation": fit_explanation,
        "hiring_recommendation": recommendation,
    }


def _llm_is_configured() -> bool:
    api_key = settings.openai_api_key or settings.llm_api_key
    if not api_key or api_key in {"your-llm-api-key", "your-openai-api-key"}:
        return False
    return bool(settings.openai_model)


def _response_endpoint() -> str:
    if settings.llm_api_url and "api.example.com" not in settings.llm_api_url:
        return settings.llm_api_url.rstrip("/")
    return f"{settings.openai_base_url.rstrip('/')}/responses"


def _extract_response_text(payload: Dict[str, Any]) -> str:
    if payload.get("output_text"):
        return payload["output_text"]

    parts = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def _call_structured_llm(
    schema_name: str,
    schema: Dict[str, Any],
    instructions: str,
    user_text: str,
    audit_prefix: str,
    max_output_tokens: int = 1000,
) -> Optional[Dict[str, Any]]:
    if not _llm_is_configured():
        log_audit_event(f"{audit_prefix}_fallback", "llm", details={"reason": "llm_not_configured"})
        return None

    body = {
        "model": settings.openai_model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": instructions}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_text}],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name,
                "strict": True,
                "schema": schema,
            }
        },
        "max_output_tokens": max_output_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key or settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    if settings.openai_project:
        headers["OpenAI-Project"] = settings.openai_project

    try:
        log_audit_event(f"{audit_prefix}_prompt_sent", "llm", details={"model": settings.openai_model})
        response = httpx.post(
            _response_endpoint(),
            headers=headers,
            json=body,
            timeout=45,
        )
        response.raise_for_status()
        payload = response.json()
        raw_text = _extract_response_text(payload)
        if not raw_text:
            raise ValueError("LLM returned empty output")
        parsed = json.loads(raw_text)
        log_audit_event(
            f"{audit_prefix}_response_received",
            "llm",
            details={"model": settings.openai_model, "keys": list(parsed.keys())},
        )
        return parsed
    except (httpx.HTTPError, ValueError, json.JSONDecodeError) as exc:
        logger.warning("LLM call failed for %s: %s", audit_prefix, exc)
        log_audit_event(f"{audit_prefix}_fallback", "llm", details={"reason": str(exc)})
        return None


def parse_resume_with_llm(resume_text: str) -> Dict[str, Any]:
    parsed = _call_structured_llm(
        schema_name="resume_parse",
        schema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "skills": {"type": "array", "items": {"type": "string"}},
                "experience_years": {"type": "number"},
                "education": {"type": "string"},
                "work_history_summary": {"type": "string"},
                "professional_summary": {"type": "string"},
            },
            "required": [
                "skills",
                "experience_years",
                "education",
                "work_history_summary",
                "professional_summary",
            ],
        },
        instructions=(
            "You extract structured hiring data from resumes. "
            "Return only valid JSON matching the schema. "
            "Normalize skills to concise labels. "
            "Estimate total experience in years as a number. "
            "Keep the professional summary to 5-7 concise lines worth of text."
        ),
        user_text=resume_text,
        audit_prefix="resume_parse",
        max_output_tokens=1200,
    )
    if not parsed:
        return _heuristic_resume_parse(resume_text)

    return {
        "skills": [skill.strip() for skill in parsed.get("skills", []) if isinstance(skill, str) and skill.strip()],
        "experience_years": float(parsed.get("experience_years", 0) or 0),
        "education": parsed.get("education") or "Not provided",
        "work_history_summary": parsed.get("work_history_summary") or "Work history not provided",
        "professional_summary": parsed.get("professional_summary") or "Summary unavailable",
    }


def enhance_job_description(job_data: Dict[str, Any]) -> Dict[str, str]:
    original = {
        "title": job_data.get("title"),
        "department": job_data.get("department"),
        "description": job_data.get("description"),
        "required_skills": job_data.get("required_skills") or [],
        "minimum_experience": job_data.get("minimum_experience"),
        "location": job_data.get("location"),
        "employment_type": job_data.get("employment_type"),
    }

    parsed = _call_structured_llm(
        schema_name="job_enhancement",
        schema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "enhanced_description": {"type": "string"},
            },
            "required": ["enhanced_description"],
        },
        instructions=(
            "You improve job descriptions for recruiters. "
            "Write a clearer, more professional, hiring-ready version. "
            "Preserve facts, avoid inventing requirements, and keep it concise and skimmable. "
            "Return only valid JSON matching the schema."
        ),
        user_text=json.dumps(original, ensure_ascii=True),
        audit_prefix="job_enhance",
        max_output_tokens=1400,
    )
    if not parsed:
        return _local_enhanced_job_description(job_data)

    return {
        "enhanced_description": parsed.get("enhanced_description") or _local_enhanced_job_description(job_data)["enhanced_description"],
    }


def generate_summary_and_fit(candidate_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, str]:
    parsed = _call_structured_llm(
        schema_name="candidate_fit_summary",
        schema={
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "summary": {"type": "string"},
                "fit_explanation": {"type": "string"},
                "hiring_recommendation": {"type": "string"},
            },
            "required": ["summary", "fit_explanation", "hiring_recommendation"],
        },
        instructions=(
            "You are assisting an HR screening workflow. "
            "Write a concise professional summary, a specific fit explanation tied to the job, "
            "and a short hiring recommendation. "
            "Do not invent credentials not present in the candidate data. "
            "Return only valid JSON matching the schema."
        ),
        user_text=json.dumps({"candidate": candidate_data, "job": job_data}, ensure_ascii=True),
        audit_prefix="summary_fit",
        max_output_tokens=900,
    )
    if not parsed:
        return _local_summary_and_fit(candidate_data, job_data)

    return {
        "summary": parsed.get("summary") or _local_summary_and_fit(candidate_data, job_data)["summary"],
        "fit_explanation": parsed.get("fit_explanation") or "Fit explanation unavailable",
        "hiring_recommendation": parsed.get("hiring_recommendation") or "Needs review",
    }
