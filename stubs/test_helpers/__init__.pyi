"""Type stubs for testing helper protocols."""

from typing import Any, Dict, Protocol


class SettingsProtocol(Protocol):
    """Protocol defining the required interface for settings objects.
    
    This protocol allows for structural typing compatibility between
    Dynaconf settings and test settings classes.
    """
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting by path using dot notation."""
        ...
    
    def as_dict(self) -> Dict[str, Any]:
        """Return settings as a dict."""
        ... 