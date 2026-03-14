# -*- coding: utf-8 -*-
"""
文件名: logging_config.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 集中式日志配置，支持控制台与按日轮转文件输出
"""
import logging
import logging.config
import logging.handlers
from pathlib import Path
from typing import Any

# 用于 CLI/非 backend 场景的简化配置
_DEFAULT_CONSOLE_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(
    log_level: str = "INFO",
    log_file: str | None = None,
    log_format: str | None = None,
    log_rotation: str = "midnight",
) -> None:
    """
    配置全局 logging，支持控制台与可选文件输出。

    Args:
        log_level: DEBUG, INFO, WARNING, ERROR
        log_file: 日志文件路径，None 则仅控制台
        log_format: 日志格式，None 使用默认
        log_rotation: midnight 按日轮转，或 size 如 10MB
    """
    fmt = log_format or _DEFAULT_CONSOLE_FORMAT
    level = getattr(logging, log_level.upper(), logging.INFO)

    handlers: dict[str, dict[str, Any]] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "default",
            "stream": "ext://sys.stderr",
        },
    }

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if "size" in log_rotation.lower():
            # 按大小轮转，如 10MB
            max_bytes = 10 * 1024 * 1024
            try:
                parts = log_rotation.lower().replace("mb", "").replace("kb", "").strip().split()
                if parts:
                    n = int(float(parts[0]))
                    if "kb" in log_rotation.lower():
                        max_bytes = n * 1024
                    else:
                        max_bytes = n * 1024 * 1024
            except (ValueError, IndexError):
                pass
            handlers["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": level,
                "formatter": "default",
                "filename": str(log_path),
                "encoding": "utf-8",
                "maxBytes": max_bytes,
                "backupCount": 5,
            }
        else:
            handlers["file"] = {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "level": level,
                "formatter": "default",
                "filename": str(log_path),
                "encoding": "utf-8",
                "when": "midnight",
                "interval": 1,
                "backupCount": 7,
            }

    root_handlers = ["console"]
    if "file" in handlers:
        root_handlers.append("file")

    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": fmt,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": handlers,
        "root": {
            "level": level,
            "handlers": root_handlers,
        },
        "loggers": {
            "uvicorn.access": {"level": "WARNING", "propagate": True},
        },
    }

    logging.config.dictConfig(config)


def setup_logging_from_settings(settings: Any) -> None:
    """
    从 Settings 对象初始化日志（backend 使用）。
    """
    setup_logging(
        log_level=getattr(settings, "log_level", "INFO"),
        log_file=getattr(settings, "log_file", None),
        log_format=getattr(settings, "log_format", None),
        log_rotation=getattr(settings, "log_rotation", "midnight"),
    )
