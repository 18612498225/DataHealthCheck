# -*- coding: utf-8 -*-
"""
文件名: main.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: FastAPI 应用入口，数据质量平台后端主程序
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.api.v1 import api_router
from app.core.logging_config import setup_logging_from_settings
from app.middleware.request_logging import RequestLoggingMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# 加载配置并初始化日志
settings = get_settings()
setup_logging_from_settings(settings)

# 日志记录器
logger = logging.getLogger(__name__)
# 创建 FastAPI 应用实例
app = FastAPI(title="Data Quality Platform API", version="1.0.0")


@app.exception_handler(Exception)
def global_exception_handler(_request: Request, exc: Exception):
    """全局异常处理器：确保未捕获的 500 错误返回 JSON 格式的详细信息"""
    if isinstance(exc, HTTPException):
        raise exc  # HTTPException 交由 FastAPI 处理
    logger.exception("未处理的异常: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# 安全响应头中间件
app.add_middleware(SecurityHeadersMiddleware)
# 请求日志中间件（记录方法、路径、状态码、耗时）
app.add_middleware(RequestLoggingMiddleware)

# 配置 CORS 跨域中间件，允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 API 路由，前缀为 /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """根路径：返回 API 基本信息"""
    return {"message": "Data Quality Platform API", "docs": "/docs"}
