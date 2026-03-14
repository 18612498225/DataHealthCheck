# -*- coding: utf-8 -*-
"""
文件名: assessment_result.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 评估结果 SQLAlchemy 模型定义
"""

# -*- coding: utf-8 -*-
"""
文件名: assessment_result.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据质量评估结果 ORM 模型定义
"""
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
