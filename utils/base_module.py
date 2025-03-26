"""Base module class for application components.

This module provides a base class that all application modules should inherit from,
providing common functionality and interface definitions.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from fastapi import FastAPI

from .config import ModuleConfig


class BaseModule(ABC):
    """Base class for all application modules."""

    def __init__(self, name: str, dependencies: Optional[list[str]] = None):
        """Initialize the base module.

        Args:
            name: Unique identifier for the module
            dependencies: List of module names this module depends on
        """
        self.name = name
        self.config = ModuleConfig(name)
        self._app: Optional[FastAPI] = None

        # Override dependencies with config if available
        if self.config.dependencies:
            self.dependencies = self.config.dependencies
        else:
            self.dependencies = dependencies or []

    @property
    def app(self) -> Optional[FastAPI]:
        """Get the FastAPI application instance."""
        return self._app

    @abstractmethod
    def init_app(self, app: FastAPI) -> None:
        """Initialize the module with a FastAPI application.

        Args:
            app: FastAPI application instance
        """
        self._app = app

    def register(self) -> None:
        """Register this module with the global registry."""
        from .registry import registry

        registry.register_module(self.name, self, self.dependencies, self.config.enabled)

    def is_enabled(self) -> bool:
        """Check if this module is enabled in the registry.

        Returns:
            True if the module is enabled, False otherwise
        """
        return self.config.enabled

    def enable(self) -> None:
        """Enable this module in the registry."""
        from .registry import registry

        registry.enable_module(self.name)

    def disable(self) -> None:
        """Disable this module in the registry."""
        from .registry import registry

        registry.disable_module(self.name)

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a module-specific setting.

        Args:
            key: Setting key to retrieve
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        return self.config.get_setting(key, default)
