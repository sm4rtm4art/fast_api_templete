"""Authentication module for the application."""

from fastapi import FastAPI

from fast_api_template.utils.base_module import BaseModule


class AuthModule(BaseModule):
    """Authentication module for the application.

    This module provides authentication functionality for the application.
    """

    def __init__(self) -> None:
        """Initialize the auth module."""
        super().__init__("auth", dependencies=[])

    def init_app(self, app: FastAPI) -> None:
        """Initialize the auth module with the FastAPI application.

        Args:
            app: The FastAPI application instance.
        """
        super().init_app(app)
        self._setup_routes(app)

    def _setup_routes(self, app: FastAPI) -> None:
        """Set up authentication routes.

        Args:
            app: The FastAPI application instance.
        """
        # Routes are already set up in routes/auth.py
        # This method exists for future extensibility
        pass
