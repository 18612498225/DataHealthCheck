"""Auth API: login, user_info."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_token, verify_password
from app.db.database import get_db
from app.models import User, Role

router = APIRouter()
security = HTTPBearer(auto_error=False)


class UserInfo(BaseModel):
    username: str
    real_name: str | None = None
    role_name: str | None = None
    org: str | None = None
    email: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: UserInfo | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


def _user_to_info(u: User, role_name: str | None = None) -> UserInfo:
    return UserInfo(
        username=u.username,
        real_name=u.real_name or u.username,
        role_name=role_name,
        org=u.org,
        email=u.email,
    )


def _do_login(username: str, password: str, db: Session) -> TokenResponse:
    user = db.query(User).filter(User.username == username).first()
    if user:
        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        role_name = None
        if user.role_id:
            role = db.query(Role).filter(Role.id == user.role_id).first()
            role_name = role.name if role else None
        token = create_access_token(username)
        return TokenResponse(access_token=token, user_info=_user_to_info(user, role_name))
    # Fallback: legacy admin/admin
    if username == "admin" and password == "admin":
        token = create_access_token("admin")
        return TokenResponse(
            access_token=token,
            user_info=UserInfo(username="admin", real_name="管理员", role_name="管理员"),
        )
    raise HTTPException(status_code=401, detail="用户名或密码错误")


@router.get("/ping")
def auth_ping():
    """Health check for auth module."""
    return {"status": "ok"}


@router.get("/me", response_model=UserInfo | None)
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user info from token."""
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
def login_json(body: LoginRequest, db: Session = Depends(get_db)):
    try:
        return _do_login(body.username, body.password, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/form", response_model=TokenResponse)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return _do_login(form.username, form.password, db)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str | None:
    """Optional auth: returns username if valid token, else None."""
    if not credentials:
        return None
    user = verify_token(credentials.credentials)
    return user
