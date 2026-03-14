"""Auth: token, password hashing."""
import os

try:
    import bcrypt
    _has_bcrypt = True
except ImportError:
    _has_bcrypt = False

DEFAULT_USER = os.environ.get("AUTH_USER", "admin")
DEFAULT_PASS = os.environ.get("AUTH_PASS", "admin")

_MVP_TOKEN = "admin-session-token"


def hash_password(plain: str) -> str:
    if _has_bcrypt:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return "plain:" + plain  # fallback for no bcrypt


def verify_password(plain: str, hashed: str) -> bool:
    if hashed.startswith("plain:"):
        return plain == hashed[6:]
    if _has_bcrypt:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    return False


def create_access_token(subject: str, expires_delta=None) -> str:
    return f"{_MVP_TOKEN}-{subject}"


def verify_token(token: str) -> str | None:
    if not token or not token.startswith(_MVP_TOKEN + "-"):
        return None
    return token[len(_MVP_TOKEN) + 1:]
