"""Testing helper protocols and utilities.

This module defines protocols and interfaces used across test modules
to ensure proper typing and consistency.
"""

from typing import Any, Dict, Protocol


class SettingsProtocol(Protocol):
    """Protocol defining the required interface for settings objects.

    This protocol allows for structural typing compatibility between
    Dynaconf settings and test settings classes.
    """

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting by path using dot notation."""
        pass

    def as_dict(self) -> Dict[str, Any]:
        """Return settings as a dict."""
        pass
