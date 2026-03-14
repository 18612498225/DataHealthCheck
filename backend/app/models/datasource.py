# -*- coding: utf-8 -*-
"""
文件名: datasource.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据源 SQLAlchemy 模型定义
"""

# -*- coding: utf-8 -*-
"""
文件名: datasource.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据源 ORM 模型定义
"""
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class Datasource(Base):
    __tablename__ = "datasources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(128), nullable=False)
    source_type = Column(String(32), nullable=False, default="csv")
    config = Column(Text, nullable=False)  # JSON string
    business_scenario = Column(String(64), nullable=True)  # 业务场景：金融信贷、政务人口、电商订单等
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
