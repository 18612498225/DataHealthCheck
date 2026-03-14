# -*- coding: utf-8 -*-
"""
文件名: users.py
编辑时间: 2025-03-14
代码编写人: Lambert tang
描述: 用户管理 API（仅管理员可操作）
"""
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.models import User, Role
from app.core.security import hash_password
from app.api.v1.auth import get_current_user

router = APIRouter()


def require_admin(username: Optional[str] = Depends(get_current_user), db: Session = Depends(get_db)) -> str:
    """校验管理员角色"""
    if not username:
        raise HTTPException(status_code=401, detail="请先登录")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=403, detail="权限不足")
    role = db.query(Role).filter(Role.id == user.role_id).first() if user.role_id else None
    if not role or role.name != "管理员":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return username


def _validate_password_strength(v: str) -> str:
    """密码至少 8 位，含字母和数字"""
    if len(v) < 8:
        raise ValueError("密码至少 8 位")
    if not re.search(r"[a-zA-Z]", v) or not re.search(r"\d", v):
        raise ValueError("密码须包含字母和数字")
    return v


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    org: Optional[str] = None
    role_id: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return _validate_password_strength(v)


class UserUpdate(BaseModel):
    real_name: Optional[str] = None
    email: Optional[str] = None
    org: Optional[str] = None
    role_id: Optional[str] = None
    password: Optional[str] = None


class UserOut(BaseModel):
    id: str
    username: str
    real_name: Optional[str] = None
    email: Optional[str] = None
    org: Optional[str] = None
    role_id: Optional[str] = None
    role_name: Optional[str] = None

    class Config:
        from_attributes = True


class RoleOut(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    """获取所有角色列表"""
    roles = db.query(Role).all()
    return [RoleOut(id=r.id, name=r.name) for r in roles]


@router.get("", response_model=list[UserOut])
def list_users(_admin: str = Depends(require_admin), db: Session = Depends(get_db)):
    """获取所有用户列表（仅管理员）"""
    users = db.query(User).all()
    result = []
    for u in users:
        role_name = None
        if u.role_id:
            role = db.query(Role).filter(Role.id == u.role_id).first()
            role_name = role.name if role else None
        result.append(UserOut(
            id=u.id,
            username=u.username,
            real_name=u.real_name,
            email=u.email,
            org=u.org,
            role_id=u.role_id,
            role_name=role_name,
        ))
    return result


@router.post("", response_model=UserOut)
def create_user(d: UserCreate, _admin: str = Depends(require_admin), db: Session = Depends(get_db)):
    """创建用户（仅管理员）"""
    if db.query(User).filter(User.username == d.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=d.username,
        password_hash=hash_password(d.password),
        real_name=d.real_name,
        email=d.email,
        org=d.org,
        role_id=d.role_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    role_name = None
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        role_name = role.name if role else None
    return UserOut(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        org=user.org,
        role_id=user.role_id,
        role_name=role_name,
    )


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: str, d: UserUpdate, _admin: str = Depends(require_admin), db: Session = Depends(get_db)):
    """更新用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if d.real_name is not None:
        user.real_name = d.real_name
    if d.email is not None:
        user.email = d.email
    if d.org is not None:
        user.org = d.org
    if d.role_id is not None:
        user.role_id = d.role_id
    if d.password is not None:
        _validate_password_strength(d.password)
        user.password_hash = hash_password(d.password)
    db.commit()
    db.refresh(user)
    role_name = None
    if user.role_id:
        role = db.query(Role).filter(Role.id == user.role_id).first()
        role_name = role.name if role else None
    return UserOut(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        org=user.org,
        role_id=user.role_id,
        role_name=role_name,
    )


@router.delete("/{user_id}")
def delete_user(user_id: str, admin_username: str = Depends(require_admin), db: Session = Depends(get_db)):
    """删除用户（仅管理员），不能删除当前登录用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    current = db.query(User).filter(User.username == admin_username).first()
    if current and current.id == user.id:
        raise HTTPException(status_code=400, detail="不能删除当前登录用户")
    db.delete(user)
    db.commit()
    return {"ok": True}
