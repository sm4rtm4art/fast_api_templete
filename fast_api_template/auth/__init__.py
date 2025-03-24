"""Authentication module."""

from pydantic import BaseModel

from .auth import create_access_token, get_current_user, get_password_hash, verify_password


class Token(BaseModel):
    """Token model."""

    access_token: str
    token_type: str
    refresh_token: str | None = None


__all__ = ["get_current_user", "create_access_token", "verify_password", "get_password_hash", "Token"]
