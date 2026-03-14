# -*- coding: utf-8 -*-
"""
文件名: rate_limit.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 登录接口限流，防止暴力破解
"""
import time
from collections import defaultdict
from fastapi import Request, HTTPException

# IP -> 最近请求时间列表（滑动窗口）
_login_attempts: dict[str, list[float]] = defaultdict(list)
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 60


def check_login_rate_limit(request: Request) -> None:
    """检查登录限流：每 IP 每分钟最多 MAX_ATTEMPTS 次"""
    import os
    if os.environ.get("TESTING") == "1":
        return
    client = getattr(request.client, "host", "unknown") if request.client else "unknown"
    now = time.time()
    window_start = now - _WINDOW_SECONDS

    # 清理过期记录
    attempts = _login_attempts[client]
    attempts[:] = [t for t in attempts if t > window_start]

    if len(attempts) >= _MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="登录尝试次数过多，请稍后再试")

    attempts.append(now)
