from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .datasources import router as datasources_router
from .rule_sets import router as rule_sets_router
from .tasks import router as tasks_router
from .reports import router as reports_router
from .profiling import router as profiling_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(datasources_router, prefix="/datasources", tags=["datasources"])
api_router.include_router(rule_sets_router, prefix="/rule-sets", tags=["rule-sets"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(profiling_router, prefix="/profiling", tags=["profiling"])
