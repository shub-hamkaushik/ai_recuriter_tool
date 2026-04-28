from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models import Base

class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    skill_match_score = Column(Float)  # Percentage
    experience_match_score = Column(Float)  # Percentage
    overall_score = Column(Float)  # Weighted score
    fit_explanation = Column(Text)
    hiring_recommendation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    candidate = relationship("Candidate")
    job = relationship("JobDescription")
