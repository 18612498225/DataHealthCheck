from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    datasource_id = Column(String(36), ForeignKey("datasources.id"), nullable=True)  # legacy migration only, use datasource_ids
    datasource_ids = Column(String(512), nullable=True)  # JSON array of datasource ids for multi-source assessment
    datasource_rule_mappings = Column(String(2048), nullable=True)  # JSON: [{"datasource_id":"xx","rule_set_id":"yy"}]
    rule_set_id = Column(String(36), ForeignKey("rule_sets.id"), nullable=True)  # legacy / first mapping
    status = Column(String(32), nullable=False, default="pending")
    trigger_type = Column(String(32), nullable=False, default="manual")
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
