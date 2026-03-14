# -*- coding: utf-8 -*-
"""
文件名: user.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 用户 SQLAlchemy 模型定义
"""

# -*- coding: utf-8 -*-
"""
文件名: user.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 用户 ORM 模型定义
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    real_name = Column(String(64), nullable=True)
    email = Column(String(128), nullable=True)
    org = Column(String(128), nullable=True)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
