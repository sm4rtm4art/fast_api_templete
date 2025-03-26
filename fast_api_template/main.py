"""Main application module.

This module initializes the FastAPI application and configures all registered modules.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .services.auth_module import AuthModule
from .utils.registry import registry


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title="FastAPI Template",
        description="A template for FastAPI applications with modular architecture",
        version="1.0.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register modules
    auth_module = AuthModule()
    auth_module.register()

    # Initialize all registered modules
    registry.initialize_app(app)

    return app
