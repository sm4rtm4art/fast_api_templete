# Module System

The FastAPI Template uses a modular architecture with a registry pattern and configuration management.

## Overview

The module system provides:

- Dynamic module registration and management
- Configuration management using Dynaconf
- Environment-specific settings
- Dependency management between modules
- Easy module enable/disable functionality

## Module Structure

Each module should:

1. Inherit from `BaseModule`
2. Implement the `init_app` method
3. Register itself with the registry
4. Have its own configuration file

### Example Module

```python
from fast_api_template.utils.base_module import BaseModule

class MyModule(BaseModule):
    def __init__(self):
        super().__init__("my_module")

    def init_app(self, app: FastAPI) -> None:
        super().init_app(app)
        # Add your module's endpoints and logic here
```

## Configuration

Each module can have its own configuration file in the `config/` directory:

```toml
[default]
my_module.enabled = true
my_module.dependencies = ["auth"]
my_module.settings = {
    "setting1": "value1",
    "setting2": "value2"
}

[development]
my_module.settings.setting1 = "dev_value"

[production]
my_module.settings.setting1 = "prod_value"
```

### Configuration Features

- Environment-specific settings
- Type validation
- Default values
- Environment variable overrides
- Secret management

### Accessing Settings

```python
class MyModule(BaseModule):
    def __init__(self):
        super().__init__("my_module")
        self.my_setting = self.get_setting("setting1", "default")
```

## Registry Pattern

The registry pattern provides:

- Central module management
- Dependency resolution
- Module lifecycle management
- Easy module discovery

### Using the Registry

```python
from fast_api_template.utils.registry import registry

# Get a module
auth_module = registry.get_module("auth")

# Check if module is enabled
if registry.is_module_enabled("auth"):
    # Use the module
    pass

# Get module dependencies
deps = registry.get_dependencies("auth")
```

## Best Practices

1. **Module Configuration**

   - Keep configuration in separate files
   - Use environment-specific settings
   - Validate configuration values
   - Use secrets for sensitive data

2. **Module Dependencies**

   - Declare dependencies explicitly
   - Avoid circular dependencies
   - Use configuration for dependency management

3. **Module Initialization**

   - Initialize in the correct order
   - Handle initialization failures gracefully
   - Clean up resources when disabled

4. **Testing**
   - Test module configuration
   - Test module initialization
   - Test dependency resolution
   - Test enable/disable functionality
