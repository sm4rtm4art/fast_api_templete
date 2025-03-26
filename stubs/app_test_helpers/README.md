# Test Helper Protocols

This directory contains Protocol classes that define interfaces used for testing purposes.
These protocols help establish structural typing relationships between production code
and test doubles.

## Protocols vs Abstract Base Classes

We use Protocol classes instead of Abstract Base Classes (ABCs) for several reasons:

1. **Structural Typing**: Protocols are based on structural typing (duck typing), meaning
   that a class doesn't need to explicitly inherit from a Protocol to be compatible with it
2. **Non-invasive**: Test code doesn't need to import or depend on production interfaces
3. **Flexibility**: Protocols can be applied retroactively to existing code without modification
4. **Testing Focus**: Protocols let us define only the methods and properties needed for testing

## Available Protocols

### `SettingsProtocol`

A Protocol that defines the minimal interface required for settings-like objects that can be
used with the CloudConfig class. This allows us to create lightweight test settings without
needing to implement all of Dynaconf's functionality.

Example usage:

```python
from typing import Any, Dict

class TestSettings:
    """Minimal test settings class."""

    def __init__(self, settings_dict: Dict[str, Any]) -> None:
        self._settings = settings_dict

    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting by path with dot notation."""
        parts = key.split('.')
        current = self._settings

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def as_dict(self) -> Dict[str, Any]:
        """Return all settings as a dictionary."""
        return self._settings

# Can be used with CloudConfig even though it doesn't inherit from anything
test_settings = TestSettings({"cloud": {"provider": "aws"}})
cloud_config = CloudConfig(test_settings)  # Type checks successfully
```

## Best Practices for Using Protocols

1. **Define Minimal Interfaces**: Only include methods/properties that are actually needed
2. **Document Usage**: Always include clear docstrings explaining the purpose
3. **Default Implementation**: Consider providing default implementations when it makes sense
4. **Type Annotations**: Use precise type annotations to improve static checking
5. **Test Coverage**: Ensure protocols are tested with different implementations
