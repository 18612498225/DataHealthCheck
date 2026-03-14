# -*- coding: utf-8 -*-
"""
文件名: security_headers.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 安全响应头中间件
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """设置安全相关 HTTP 响应头"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
