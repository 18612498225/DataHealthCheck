# -*- coding: utf-8 -*-
"""
文件名: __init__.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 注册所有 v1 API 路由
"""
from fastapi import APIRouter, Depends
from .auth import router as auth_router, require_login
from .users import router as users_router
from .datasources import router as datasources_router
from .rule_sets import router as rule_sets_router
from .tasks import router as tasks_router
from .reports import router as reports_router
from .profiling import router as profiling_router

api_router = APIRouter()
# 白名单：auth 下 login、login/form、ping 无需鉴权
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
# 以下业务 API 需登录
api_router.include_router(users_router, prefix="/users", tags=["users"], dependencies=[Depends(require_login)])
api_router.include_router(datasources_router, prefix="/datasources", tags=["datasources"], dependencies=[Depends(require_login)])
api_router.include_router(rule_sets_router, prefix="/rule-sets", tags=["rule-sets"], dependencies=[Depends(require_login)])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"], dependencies=[Depends(require_login)])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"], dependencies=[Depends(require_login)])
api_router.include_router(profiling_router, prefix="/profiling", tags=["profiling"], dependencies=[Depends(require_login)])
