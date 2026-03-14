# -*- coding: utf-8 -*-
"""
文件名: config.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 应用配置模块，数据库连接、CORS、JWT 等配置
"""
import secrets
from pathlib import Path
from pydantic_settings import BaseSettings
from functools import lru_cache

# 默认数据库路径：backend/app.db
_backend_dir = Path(__file__).resolve().parent.parent
_default_db = _backend_dir / "app.db"


class Settings(BaseSettings):
    """应用配置类"""

    database_url: str = f"sqlite:///{_default_db.as_posix()}"  # 数据库连接地址
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"  # 允许的跨域来源

    # JWT 配置
    secret_key: str = ""  # 生产环境必须通过 SECRET_KEY 环境变量配置
    access_token_expire_minutes: int = 60 * 24  # 24 小时

    # 日志配置
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_file: str | None = None  # 如 logs/app.log，None 则仅控制台
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    log_rotation: str = "midnight"  # midnight 按日轮转

    class Config:
        env_file = ".env"  # 从 .env 文件加载环境变量


@lru_cache
def get_settings() -> Settings:
    """获取配置单例（带缓存）"""
    return Settings()
