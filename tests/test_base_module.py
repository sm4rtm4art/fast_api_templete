"""Tests for the base module with configuration integration."""

import pytest
from fastapi import FastAPI

from fast_api_template.utils.base_module import BaseModule


# Use a factory function instead of a class to avoid the warning
def create_test_module(name: str = "test_module") -> BaseModule:
    """Create a test module instance with custom behavior."""
    module = BaseModule(name)

    # Add resources attribute
    setattr(module, "resources", [])

    # Add the custom init_app method using monkey patching
    original_init_app = module.init_app

    def custom_init_app(app: FastAPI) -> None:
        original_init_app(app)
        # Access resources property via getattr to avoid mypy error
        setattr(module, "resources", [])

    # Use proper method for replacing the init_app method
    setattr(module, "init_app", custom_init_app)

    return module


class DependentModule(BaseModule):
    """Module that depends on TestModule."""

    def __init__(self) -> None:
        """Initialize the dependent module."""
        super().__init__("dependent_module", dependencies=["test_module"])
        self.initialized: bool = False

    def init_app(self, app: FastAPI) -> None:
        """Initialize the dependent module."""
        super().init_app(app)
        self.initialized = True


@pytest.fixture
def test_module() -> BaseModule:
    """Create a test module instance."""
    return create_test_module("test_module")


@pytest.fixture
def dependent_module() -> DependentModule:
    """Create a dependent module instance."""
    return DependentModule()


@pytest.fixture
def app() -> FastAPI:
    """Create a FastAPI application instance."""
    return FastAPI()


def test_module_initialization(test_module: BaseModule) -> None:
    """Test module initialization."""
    assert test_module.name == "test_module"
    assert test_module.dependencies == []
    assert test_module.config is not None
    assert test_module.app is None
    assert not test_module._initialized


def test_module_config_integration(test_module: BaseModule) -> None:
    """Test module configuration integration."""
    test_module.register()
    test_module.enable()
    assert test_module.is_enabled() == test_module.config.enabled
    assert test_module.dependencies == test_module.config.dependencies


def test_module_app_initialization(test_module: BaseModule, app: FastAPI) -> None:
    """Test module app initialization."""
    test_module.init_app(app)
    assert test_module.app == app
    assert test_module._initialized


def test_module_registration(test_module: BaseModule) -> None:
    """Test module registration."""
    test_module.register()
    assert test_module.is_enabled() == test_module.config.enabled


def test_module_enable_disable(test_module: BaseModule) -> None:
    """Test module enable/disable functionality."""
    test_module.register()
    test_module.enable()
    assert test_module.is_enabled()
    test_module.disable()
    assert not test_module.is_enabled()


def test_module_settings(test_module: BaseModule) -> None:
    """Test module settings access."""
    assert test_module.get_setting("test_key") == "test_value"
    assert test_module.get_setting("nested.key") == "value"
    assert test_module.get_setting("non_existent", "default") == "default"


def test_dependent_module_initialization(dependent_module: DependentModule) -> None:
    """Test dependent module initialization."""
    assert dependent_module.name == "dependent_module"
    assert dependent_module.dependencies == ["test_module"]
    assert dependent_module.config is not None
    assert dependent_module.app is None
    assert not dependent_module._initialized


def test_dependent_module_registration(dependent_module: DependentModule) -> None:
    """Test dependent module registration."""
    dependent_module.register()
    assert dependent_module.dependencies == ["test_module"]


def test_module_cleanup(test_module: BaseModule) -> None:
    """Test module cleanup."""
    # Set resources attribute
    setattr(test_module, "resources", [])
    test_module.cleanup()
    assert not hasattr(test_module, "resources")


def test_module_reinitialization(test_module: BaseModule, app: FastAPI) -> None:
    """Test module reinitialization."""
    test_module.init_app(app)
    new_app = FastAPI()
    test_module.init_app(new_app)
    assert test_module.app == new_app


def test_module_config_override(test_module: BaseModule) -> None:
    """Test module configuration override."""
    test_module.register()
    assert test_module.is_enabled() == test_module.config.enabled
