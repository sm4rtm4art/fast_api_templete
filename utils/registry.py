"""Module registry for managing application components.

This module provides a central registry for managing different components
of the application, allowing for dynamic loading and management of features.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import FastAPI


@dataclass
class ModuleInfo:
    """Information about a registered module."""

    name: str
    module: Any
    dependencies: list[str]
    enabled: bool = True


class ModuleRegistry:
    """Central registry for managing application modules."""

    _instance: Optional["ModuleRegistry"] = None
    _modules: Dict[str, ModuleInfo] = {}

    def __new__(cls) -> "ModuleRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register_module(
        self, name: str, module: Any, dependencies: Optional[list[str]] = None, enabled: bool = True
    ) -> None:
        """Register a new module in the registry.

        Args:
            name: Unique identifier for the module
            module: The module instance or class to register
            dependencies: List of module names this module depends on
            enabled: Whether the module is enabled by default
        """
        if dependencies is None:
            dependencies = []

        self._modules[name] = ModuleInfo(name=name, module=module, dependencies=dependencies, enabled=enabled)

    def get_module(self, name: str) -> Optional[Any]:
        """Retrieve a registered module by name.

        Args:
            name: Name of the module to retrieve

        Returns:
            The registered module or None if not found
        """
        module_info = self._modules.get(name)
        return module_info.module if module_info else None

    def is_module_enabled(self, name: str) -> bool:
        """Check if a module is enabled.

        Args:
            name: Name of the module to check

        Returns:
            True if the module is enabled, False otherwise
        """
        module_info = self._modules.get(name)
        return module_info.enabled if module_info else False

    def enable_module(self, name: str) -> None:
        """Enable a registered module.

        Args:
            name: Name of the module to enable
        """
        if name in self._modules:
            self._modules[name].enabled = True

    def disable_module(self, name: str) -> None:
        """Disable a registered module.

        Args:
            name: Name of the module to enable
        """
        if name in self._modules:
            self._modules[name].enabled = False

    def get_dependencies(self, name: str) -> list[str]:
        """Get the dependencies for a module.

        Args:
            name: Name of the module

        Returns:
            List of dependency module names
        """
        module_info = self._modules.get(name)
        return module_info.dependencies if module_info else []

    def initialize_app(self, app: FastAPI) -> None:
        """Initialize all enabled modules with the FastAPI application.

        Args:
            app: FastAPI application instance
        """
        for _name, module_info in self._modules.items():
            if module_info.enabled:
                if hasattr(module_info.module, "init_app"):
                    module_info.module.init_app(app)


# Create a global registry instance
registry = ModuleRegistry()
