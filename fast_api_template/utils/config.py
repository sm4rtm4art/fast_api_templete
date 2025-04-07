"""Configuration management for application modules."""

import os
from typing import Any, Dict, Generic, List, Optional, TypeVar, cast

from pydantic import BaseModel, Field

# Type variables for better IDE support
T = TypeVar("T", bound=BaseModel)


class ModuleSettings(BaseModel):
    """Base module settings class."""

    enabled: bool = False
    dependencies: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)


class PydanticModuleConfig(Generic[T]):
    """Configuration for application modules using Pydantic Settings."""

    def __init__(self, name: str, settings: Optional[T] = None) -> None:
        """Initialize the module configuration.

        Args:
            name: The name of the module.
            settings: Optional settings instance to use
        """
        self.name = name
        self._env = os.getenv("FAST_API_TEMPLATE_ENV", "DEVELOPMENT").lower()

        # If settings aren't provided, create default settings
        if settings is None:
            # Create a base settings model for this module
            self._settings = ModuleSettings(enabled=False, dependencies=[], settings={})
        else:
            # Use type casting to help mypy understand that T can be used as _settings
            self._settings = cast(ModuleSettings, settings)

    @property
    def enabled(self) -> bool:
        """Get whether the module is enabled.

        Returns:
            bool: True if the module is enabled, False otherwise.
        """
        return getattr(self._settings, "enabled", False)

    @property
    def dependencies(self) -> List[str]:
        """Get the module dependencies.

        Returns:
            List[str]: List of module names this module depends on.
        """
        return getattr(self._settings, "dependencies", [])

    @property
    def settings(self) -> Dict[str, Any]:
        """Get the module settings.

        Returns:
            Dict[str, Any]: Dictionary of module settings.
        """
        # Get settings for the current environment
        return getattr(self._settings, "settings", {})

    def _resolve_nested_key(self, settings_dict: dict, key: str, default: Any) -> Any:
        """Resolve a nested key in settings dictionary."""
        if "." not in key:
            return settings_dict.get(key, default)

        parts = key.split(".")
        value: Any = settings_dict
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value.get(part)
            else:
                return default
        return value

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a module setting.

        Args:
            key: The setting key.
            default: Default value if setting is not found.

        Returns:
            Any: The setting value.
        """
        # Fall back to settings dictionary
        return self._resolve_nested_key(self.settings, key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """Set a module setting.

        Args:
            key: The setting key.
            value: The setting value.
        """
        if not hasattr(self._settings, "settings"):
            self._settings.settings = {}

        current_settings = self.settings

        if "." in key:
            # Handle nested settings
            parts = key.split(".")
            current = dict(current_settings)
            settings_dict = current
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current.setdefault(part, {})
            current[parts[-1]] = value
            self._settings.settings = settings_dict
        else:
            # Make a copy to avoid modifying the original
            settings_dict = dict(current_settings)
            settings_dict[key] = value
            self._settings.settings = settings_dict


# For backwards compatibility
ModuleConfig = PydanticModuleConfig


def create_module_config(name: str) -> PydanticModuleConfig:
    """Create a module configuration.

    Args:
        name: The name of the module.

    Returns:
        PydanticModuleConfig: The module configuration.
    """
    # Get the current environment
    env = os.getenv("FAST_API_TEMPLATE_ENV", "DEVELOPMENT")
    print(f"Creating module config for {name} in environment: {env}")

    # Create a basic module configuration
    return PydanticModuleConfig(name=name)
