# -*- coding: utf-8 -*-
"""
文件名: rule_set.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 规则集 Pydantic Schema 定义
"""

# -*- coding: utf-8 -*-
"""
文件名: rule_set.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 规则集相关的 Pydantic 请求/响应 Schema
"""
from pydantic import BaseModel
from typing import Optional, List, Any


class RuleSetBase(BaseModel):
    name: str
    description: Optional[str] = None
    rules: List[dict[str, Any]]
    industry: Optional[str] = None
    quality_dimensions: Optional[List[str]] = None
    standard_ref: Optional[str] = None


class RuleSetCreate(RuleSetBase):
    pass


class RuleSetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[List[dict[str, Any]]] = None
    industry: Optional[str] = None
    quality_dimensions: Optional[List[str]] = None
    standard_ref: Optional[str] = None


class RuleSetResponse(RuleSetBase):
    id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
