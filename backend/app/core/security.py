# -*- coding: utf-8 -*-
"""
文件名: security.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 认证安全模块，JWT 生成与校验、密码哈希
"""
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt import PyJWTError

from app.config import get_settings


_secret_key_cache: str | None = None


def _get_secret_key() -> str:
    global _secret_key_cache
    s = get_settings()
    if s.secret_key:
        return s.secret_key
    if _secret_key_cache is None:
        _secret_key_cache = secrets.token_hex(32)
    return _secret_key_cache


def hash_password(plain: str) -> str:
    """对明文密码进行 bcrypt 哈希"""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码与哈希是否匹配"""
    if hashed.startswith("plain:"):
        return False  # 拒绝旧版明文存储
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """创建 JWT access token，带 exp、iat、sub"""
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + exp,
    }
    return jwt.encode(payload, _get_secret_key(), algorithm="HS256")


def verify_token(token: str) -> str | None:
    """验证 JWT 签名与过期，返回 subject 或 None"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=["HS256"])
        sub = payload.get("sub")
        return str(sub) if sub else None
    except PyJWTError:
        return None
