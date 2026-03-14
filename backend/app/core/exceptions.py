# -*- coding: utf-8 -*-
"""
文件名: exceptions.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 应用自定义异常类
"""


class AppException(Exception):
    """应用基础异常"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppException):
    """资源未找到异常"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(AppException):
    """校验失败异常"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)
