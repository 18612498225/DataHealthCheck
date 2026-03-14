# -*- coding: utf-8 -*-
"""
文件名: auth.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 认证 API，提供登录、用户信息接口
"""
import logging
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_token, verify_password
from app.db.database import get_db
from app.models import User, Role
from app.middleware.rate_limit import check_login_rate_limit

router = APIRouter()
security = HTTPBearer(auto_error=False)


class UserInfo(BaseModel):
    """用户信息模型"""
    username: str
    real_name: str | None = None
    role_name: str | None = None
    org: str | None = None
    email: str | None = None


class TokenResponse(BaseModel):
    """登录响应模型：包含 token 和用户信息"""
    access_token: str
    token_type: str = "bearer"
    user_info: UserInfo | None = None


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


def _user_to_info(u: User, role_name: str | None = None) -> UserInfo:
    """将 User 模型转换为 UserInfo 响应"""
    return UserInfo(
        username=u.username,
        real_name=u.real_name or u.username,
        role_name=role_name,
        org=u.org,
        email=u.email,
    )


def _do_login(username: str, password: str, db: Session) -> TokenResponse:
    """执行登录逻辑：验证用户密码并生成 JWT token"""
    user = db.query(User).filter(User.username == username).first()
    if user:
        if not verify_password(password, user.password_hash):
            logger.info("登录失败: 用户 %s 密码错误", username)
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        role_name = None
        if user.role_id:
            role = db.query(Role).filter(Role.id == user.role_id).first()
            role_name = role.name if role else None
        token = create_access_token(username)
        logger.info("登录成功: 用户 %s", username)
        return TokenResponse(access_token=token, user_info=_user_to_info(user, role_name))
    logger.info("登录失败: 用户 %s 不存在", username)
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@router.get("/ping")
def auth_ping():
    """认证模块健康检查"""
    return {"status": "ok"}


@router.get("/me", response_model=UserInfo | None)
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """从 token 获取当前用户信息"""
    if not credentials:
        return None
    username = verify_token(credentials.credentials)
    if not username:
        return None
    user = db.query(User).filter(User.username == username).first()
    if user:
        role_name = None
        if user.role_id:
            role = db.query(Role).filter(Role.id == user.role_id).first()
            role_name = role.name if role else None
        return _user_to_info(user, role_name)
    return UserInfo(username=username, real_name=username)


@router.post("/login", response_model=TokenResponse)
def login_json(body: LoginRequest, db: Session = Depends(get_db), _: None = Depends(check_login_rate_limit)):
    try:
        return _do_login(body.username, body.password, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/form", response_model=TokenResponse)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), _: None = Depends(check_login_rate_limit)):
    return _do_login(form.username, form.password, db)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str | None:
    """可选认证：token 有效则返回用户名，否则返回 None"""
    if not credentials:
        return None
    return verify_token(credentials.credentials)


def require_login(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """强制认证：token 无效时返回 401"""
    if not credentials:
        raise HTTPException(status_code=401, detail="请先登录")
    username = verify_token(credentials.credentials)
    if not username:
        raise HTTPException(status_code=401, detail="无效或过期的 token，请重新登录")
    return username
