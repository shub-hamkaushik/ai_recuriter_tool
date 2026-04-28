from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime
from sqlalchemy.sql import func
from app.models import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    experience_years = Column(Float)
    parsed_skills = Column(JSON)  # List of skills from LLM
    raw_resume_text = Column(Text)
    resume_filename = Column(String)
    status = Column(String, default="New")
    education_details = Column(Text)
    work_history_summary = Column(Text)
    ai_summary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
