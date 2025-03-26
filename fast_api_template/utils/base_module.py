"""Base module class for application modules."""

from typing import Any, List, Optional, Type, TypeVar

from fastapi import FastAPI

from fast_api_template.utils.config import create_module_config
from fast_api_template.utils.module_registry import registry

T = TypeVar("T", bound="BaseModule")


class BaseModule:
    """Base class for application modules."""

    def __init__(self, name: str, dependencies: Optional[List[str]] = None) -> None:
        """Initialize the module.

        Args:
            name: The name of the module.
            dependencies: List of module names this module depends on.
        """
        self.name = name
        self.dependencies = dependencies or []
        self.config = create_module_config(name)
        self.app: Optional[FastAPI] = None
        self._initialized = False

        # Override dependencies with config if available
        if self.config and self.config.dependencies:
            self.dependencies = self.config.dependencies

    @classmethod
    def create(cls: Type[T], name: str, dependencies: Optional[List[str]] = None) -> T:
        """Factory method to create a module instance.

        Args:
            name: The name of the module.
            dependencies: List of module names this module depends on.

        Returns:
            An instance of the module class.
        """
        return cls(name, dependencies)

    def init_app(self, app: FastAPI) -> None:
        """Initialize the module with the FastAPI application.

        Args:
            app: The FastAPI application instance.
        """
        self.app = app
        self._initialized = True

    def register(self) -> None:
        """Register the module with the registry."""
        registry.register_module(self)
        if self.config.enabled:
            self.enable()

    def enable(self) -> None:
        """Enable the module."""
        registry.enable_module(self.name)

    def disable(self) -> None:
        """Disable the module."""
        registry.disable_module(self.name)

    def is_enabled(self) -> bool:
        """Check if the module is enabled.

        Returns:
            bool: True if the module is enabled, False otherwise.
        """
        return registry.is_module_enabled(self.name) and self.config.enabled

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a module setting.

        Args:
            key: The setting key.
            default: Default value if setting is not found.

        Returns:
            Any: The setting value.
        """
        if self.config:
            return self.config.get_setting(key, default)
        return default

    def cleanup(self) -> None:
        """Clean up module resources."""
        if hasattr(self, "resources"):
            delattr(self, "resources")
