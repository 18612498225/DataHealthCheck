# -*- coding: utf-8 -*-
"""
文件名: task.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 任务相关 Pydantic Schema 定义
"""

# -*- coding: utf-8 -*-
"""
文件名: task.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 任务相关的 Pydantic 请求/响应 Schema
"""
from pydantic import BaseModel
from typing import Optional, List, Any


class TaskRun(BaseModel):
    name: str
    datasource_ids: Optional[list[str]] = None  # one or more datasource ids
    rule_set_id: Optional[str] = None  # used when datasource_rule_mappings not provided
    datasource_rule_mappings: Optional[list[dict]] = None  # [{"datasource_id":"xx","rule_set_id":"yy"}]


class TaskResponse(BaseModel):
    id: str
    name: str
    datasource_ids: list[str] | None = None
    rule_set_id: Optional[str] = None
    status: str
    trigger_type: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class TaskDetail(TaskResponse):
    result: Optional[dict[str, Any]] = None
