from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    summary = Column(Text, nullable=False)  # JSON: {total, passed, failed}
    details = Column(Text, nullable=False)  # JSON array
    report_html = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
