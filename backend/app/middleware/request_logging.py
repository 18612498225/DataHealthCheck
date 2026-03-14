# -*- coding: utf-8 -*-
"""
文件名: request_logging.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 请求日志中间件，记录方法、路径、状态码、耗时、客户端 IP
"""
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

# 不记录日志的路径
_SKIP_PATHS = {"/docs", "/redoc", "/openapi.json", "/favicon.ico"}


def _should_skip(path: str) -> bool:
    return any(path.startswith(p) or path == p for p in _SKIP_PATHS)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """记录 HTTP 请求的中间件：方法、路径、状态码、耗时、客户端 IP"""

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if _should_skip(path):
            return await call_next(request)

        method = request.method
        client = getattr(request.client, "host", "unknown") if request.client else "unknown"
        start = time.perf_counter()

        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        status = response.status_code

        msg = "%s %s %s %.1fms %s" % (method, path, status, elapsed, client)
        if status >= 500:
            logger.error(msg)
        elif status >= 400:
            logger.warning(msg)
        else:
            logger.info(msg)

        return response
