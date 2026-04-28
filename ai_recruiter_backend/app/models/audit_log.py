from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.models import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True, nullable=False)
    entity_type = Column(String, index=True)
    entity_id = Column(String)
    actor = Column(String)
    details = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
