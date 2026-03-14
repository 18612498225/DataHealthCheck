# -*- coding: utf-8 -*-
"""
文件名: role.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 角色 SQLAlchemy 模型定义
"""

# -*- coding: utf-8 -*-
"""
文件名: role.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 角色/权限 ORM 模型定义
"""
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
