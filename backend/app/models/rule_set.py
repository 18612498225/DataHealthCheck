# -*- coding: utf-8 -*-
"""
文件名: rule_set.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 规则集 SQLAlchemy 模型定义，支持行业/标准建模
"""

# -*- coding: utf-8 -*-
"""
文件名: rule_set.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 规则集 ORM 模型定义，支持行业与标准引用
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class RuleSet(Base):
    __tablename__ = "rule_sets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    rules = Column(Text, nullable=False)  # JSON array string
    # Industry/standard modeling (DAMA-DMBOK, GB/T 36344, DCMM)
    industry = Column(String(64), nullable=True, default=None)  # e.g. 通用, 金融, 政务
    quality_dimensions = Column(Text, nullable=True, default=None)  # JSON array e.g. ["completeness","uniqueness"]
    standard_ref = Column(String(128), nullable=True, default=None)  # e.g. GB/T 36344-2018, DAMA-DMBOK
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
