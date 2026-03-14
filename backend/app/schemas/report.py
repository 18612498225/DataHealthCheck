# -*- coding: utf-8 -*-
"""
文件名: report.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 报告响应 Pydantic Schema 定义
"""

# -*- coding: utf-8 -*-
"""
文件名: report.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 评估报告相关的 Pydantic 响应 Schema
"""
from pydantic import BaseModel
from typing import List, Any


class ReportResponse(BaseModel):
    task_id: str
    summary: dict[str, int]
    details: List[dict[str, Any]]
