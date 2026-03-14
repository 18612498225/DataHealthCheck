from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(64), nullable=False)
    permissions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
