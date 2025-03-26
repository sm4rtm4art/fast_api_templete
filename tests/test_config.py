"""Tests for the configuration system."""

import os

import pytest

from fast_api_template.utils.config import ModuleConfig, create_module_config


@pytest.fixture
def module_config() -> ModuleConfig:
    """Create a test module configuration."""
    return create_module_config("test_module")


def test_create_module_config() -> None:
    """Test creating a module configuration."""
    test_module_config = create_module_config("test_module")
    assert isinstance(test_module_config, ModuleConfig)


def test_module_config_properties(module_config: ModuleConfig) -> None:
    """Test module configuration properties."""
    assert module_config.enabled is True
    assert module_config.dependencies == []
    expected_settings = {"test_key": "test_value", "nested": {"key": "value"}}
    assert module_config.settings == expected_settings


def test_module_config_get_setting(module_config: ModuleConfig) -> None:
    """Test getting module settings."""
    assert module_config.get_setting("test_key") == "test_value"
    assert module_config.get_setting("nested.key") == "value"
    assert module_config.get_setting("non_existent", "default") == "default"


def test_module_config_environment_override() -> None:
    """Test environment-specific configuration overrides."""
    original_env = os.environ.get("ENV_FOR_DYNACONF")
    try:
        os.environ["ENV_FOR_DYNACONF"] = "development"
        config = create_module_config("test_module")
        assert config.get_setting("test_key") == "dev_value"

        os.environ["ENV_FOR_DYNACONF"] = "production"
        config = create_module_config("test_module")
        assert config.get_setting("test_key") == "prod_value"
    finally:
        if original_env is not None:
            os.environ["ENV_FOR_DYNACONF"] = original_env
        else:
            del os.environ["ENV_FOR_DYNACONF"]


def test_module_config_validation() -> None:
    """Test configuration validation."""
    config = create_module_config("invalid")
    # Manually set invalid values to force validation to fail
    setattr(
        config,
        "_settings",
        {"invalid.enabled": "not_a_bool", "invalid.dependencies": "not_a_list", "invalid.settings": "not_a_dict"},
    )
    with pytest.raises(ValueError):
        config._validate_config()


def test_module_config_secrets() -> None:
    """Test handling of secrets from environment variables."""
    config = create_module_config("auth")
    assert config.get_setting("secret_key") == "test_secret"


def test_module_config_file_loading() -> None:
    """Test loading configuration from files."""
    config = create_module_config("test_module")
    assert config.get_setting("test_key") == "test_value"


def test_module_config_override_priority() -> None:
    """Test configuration override priority."""
    os.environ["ENV_FOR_DYNACONF"] = "development"
    config = create_module_config("test_module")
    assert config.get_setting("test_key") == "dev_value"


def test_module_config_missing_files() -> None:
    """Test behavior when configuration files are missing."""
    config = create_module_config("non_existent_module")
    assert config.enabled is False
    assert config.dependencies == []
    assert config.settings == {}


def test_module_config_invalid_file() -> None:
    """Test handling of invalid configuration files."""
    config = create_module_config("invalid")
    # Manually set invalid values to force validation to fail
    setattr(
        config,
        "_settings",
        {"invalid.enabled": "not_a_bool", "invalid.dependencies": "not_a_list", "invalid.settings": "not_a_dict"},
    )
    with pytest.raises(ValueError):
        config._validate_config()
