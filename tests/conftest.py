# -*- coding: utf-8 -*-
"""
文件名: conftest.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: Pytest 配置与公共 fixtures
"""
import sys
from pathlib import Path

# Ensure project root is in path for data_quality_tool imports
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
