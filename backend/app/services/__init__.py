# -*- coding: utf-8 -*-
"""
文件名: __init__.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 服务层包初始化，导出数据加载、评估、报告等
"""

# -*- coding: utf-8 -*-
"""
文件名: __init__.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 服务层包初始化，导出数据加载、评估、报告生成等接口
"""
from .data_loader import load_data
from .assessment import run_assessment
from .report import build_report_json, build_report_html
