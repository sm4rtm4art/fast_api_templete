"""Authentication module for the application.

This module provides authentication functionality using the registry pattern.
"""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from fast_api_template.utils.base_module import BaseModule


class AuthModule(BaseModule):
    """Authentication module implementation."""

    def __init__(self) -> None:
        """Initialize the authentication module."""
        super().__init__("auth")
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    def init_app(self, app: FastAPI) -> None:
        """Initialize the module with FastAPI application.

        Args:
            app: FastAPI application instance
        """
        super().init_app(app)

        # Add authentication endpoints
        @app.post("/token")
        async def login(username: str, password: str) -> dict:
            """Login endpoint."""
            # Implement actual authentication logic here
            if username == "test" and password == "test":
                return {"access_token": "dummy_token", "token_type": "bearer"}
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        @app.get("/users/me")
        async def read_users_me(token: str = Depends(self.oauth2_scheme)) -> dict:
            """Get current user endpoint."""
            # Implement actual user retrieval logic here
            return {"username": "test_user"}

    async def get_current_user(self, token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))) -> dict:
        """Get the current user from a token.

        Args:
            token: OAuth2 token

        Returns:
            User information
        """
        # Implement actual token validation and user retrieval here
        return {"username": "test_user"}
