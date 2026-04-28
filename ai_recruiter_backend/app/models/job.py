from sqlalchemy import Column, Integer, String, Text, Float, JSON, DateTime
from sqlalchemy.sql import func
from app.models import Base

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    department = Column(String)
    required_skills = Column(JSON)  # List of required skills
    minimum_experience = Column(Float)  # Years
    description = Column(Text)
    location = Column(String)
    employment_type = Column(String)
    status = Column(String, default="Open")
    enhanced_description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
