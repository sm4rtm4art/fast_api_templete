"""Module registry for managing application modules."""

from typing import TYPE_CHECKING, Dict, List, Optional, Set

if TYPE_CHECKING:
    from fastapi import FastAPI

    from fast_api_template.utils.base_module import BaseModule


class ModuleRegistry:
    """Registry for managing application modules."""

    def __init__(self) -> None:
        """Initialize the module registry."""
        self._modules: Dict[str, "BaseModule"] = {}
        self._enabled_modules: Dict[str, bool] = {}
        self._dependencies: Dict[str, List[str]] = {}

    def register_module(self, module: "BaseModule") -> None:
        """Register a module with the registry.

        Args:
            module: The module to register.
        """
        self._modules[module.name] = module
        self._enabled_modules[module.name] = module.config.enabled
        self._dependencies[module.name] = module.dependencies

    def get_module(self, name: str) -> Optional["BaseModule"]:
        """Get a module by name.

        Args:
            name: The name of the module.

        Returns:
            Optional[BaseModule]: The module if found, None otherwise.
        """
        return self._modules.get(name)

    def is_module_enabled(self, name: str) -> bool:
        """Check if a module is enabled.

        Args:
            name: The name of the module.

        Returns:
            bool: True if the module is enabled, False otherwise.
        """
        return self._enabled_modules.get(name, False)

    def enable_module(self, name: str) -> None:
        """Enable a module.

        Args:
            name: The name of the module.
        """
        if name in self._modules:
            self._enabled_modules[name] = True

    def disable_module(self, name: str) -> None:
        """Disable a module.

        Args:
            name: The name of the module.
        """
        if name in self._modules:
            self._enabled_modules[name] = False

    def get_dependencies(self, name: str) -> List[str]:
        """Get a module's dependencies.

        Args:
            name: The name of the module.

        Returns:
            List[str]: List of module names this module depends on.
        """
        return self._dependencies.get(name, [])

    def get_enabled_modules(self) -> List[str]:
        """Get all enabled module names.

        Returns:
            List[str]: List of enabled module names.
        """
        return [name for name, enabled in self._enabled_modules.items() if enabled]

    def get_disabled_modules(self) -> List[str]:
        """Get all disabled module names.

        Returns:
            List[str]: List of disabled module names.
        """
        return [name for name, enabled in self._enabled_modules.items() if not enabled]

    def initialize_app(self, app: "FastAPI") -> None:
        """Initialize all enabled modules with the FastAPI application.

        This method resolves module dependencies and initializes them in the correct order.

        Args:
            app: The FastAPI application instance.
        """
        # Track initialized modules to avoid duplicates
        initialized: Set[str] = set()

        # Initialize modules in dependency order
        for module_name in self.get_enabled_modules():
            self._initialize_module_with_dependencies(module_name, app, initialized)

    def _initialize_module_with_dependencies(self, module_name: str, app: "FastAPI", initialized: Set[str]) -> None:
        """Initialize a module and its dependencies.

        Args:
            module_name: The name of the module to initialize.
            app: The FastAPI application instance.
            initialized: Set of already initialized module names.
        """
        # Skip if already initialized
        if module_name in initialized:
            return

        # Get the module
        module = self.get_module(module_name)
        if not module or not self.is_module_enabled(module_name):
            return

        # Initialize dependencies first
        for dep_name in self.get_dependencies(module_name):
            self._initialize_module_with_dependencies(dep_name, app, initialized)

        # Initialize the module
        module.init_app(app)
        initialized.add(module_name)


# Create a singleton instance
registry = ModuleRegistry()
