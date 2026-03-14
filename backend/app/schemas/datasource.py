# -*- coding: utf-8 -*-
"""
文件名: datasource.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据源 Pydantic Schema 定义
"""

# -*- coding: utf-8 -*-
"""
文件名: datasource.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 数据源相关的 Pydantic 请求/响应 Schema
"""
from pydantic import BaseModel
from typing import Optional, Any


class DatasourceBase(BaseModel):
    name: str
    source_type: str = "csv"
    config: dict[str, Any]
    business_scenario: Optional[str] = None


class DatasourceCreate(DatasourceBase):
    pass


class DatasourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    config: Optional[dict[str, Any]] = None
    business_scenario: Optional[str] = None


class DatasourceResponse(DatasourceBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
