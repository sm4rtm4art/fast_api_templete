"""Configuration management for the application.

This module provides configuration management using Dynaconf,
allowing for dynamic loading and validation of module settings.
"""

from typing import Any, Dict

from dynaconf import Dynaconf, Validator


def create_module_config(module_name: str) -> Dynaconf:
    """Create a configuration instance for a specific module.

    Args:
        module_name: Name of the module to configure

    Returns:
        Dynaconf configuration instance
    """
    validators = [
        Validator(f"{module_name}.enabled", is_type_of=bool, default=True),
        Validator(f"{module_name}.dependencies", is_type_of=list, default=[]),
        Validator(f"{module_name}.settings", is_type_of=dict, default={}),
    ]

    return Dynaconf(
        envvar_prefix="FASTAPI",
        settings_files=[
            "settings.toml",
            ".secrets.toml",
            f"config/{module_name}.toml",
        ],
        validators=validators,
        environments=True,
        load_dotenv=True,
    )


class ModuleConfig:
    """Configuration wrapper for module settings."""

    def __init__(self, module_name: str):
        """Initialize module configuration.

        Args:
            module_name: Name of the module to configure
        """
        self.module_name = module_name
        self.config = create_module_config(module_name)

    @property
    def enabled(self) -> bool:
        """Get whether the module is enabled."""
        return self.config.get(f"{self.module_name}.enabled", False)

    @property
    def dependencies(self) -> list[str]:
        """Get module dependencies."""
        return self.config.get(f"{self.module_name}.dependencies", [])

    @property
    def settings(self) -> Dict[str, Any]:
        """Get module-specific settings."""
        return self.config.get(f"{self.module_name}.settings", {})

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value.

        Args:
            key: Setting key to retrieve
            default: Default value if setting not found

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)
