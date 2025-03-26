#!/usr/bin/env python3
"""Whitelist for vulture false positives.

This file lists functions and variables that are used dynamically or
via introspection, which vulture would otherwise report as unused.
"""
import sys


# Test mock classes and methods
class TestSettings:
    """Helper class for testing settings.

    Used in test fixtures but not directly invoked in the code.
    """

    def __init__(self):
        pass

    def get(self, key, default=None):
        """Get a setting value by key."""
        pass

    def as_dict(self):
        """Return settings as a dict."""
        pass


# Mock variables and return values from test fixtures
mock_method = None
mock_props = None
mock_body = None
mock_return_value = None
mock_return_value__call__ = None


# Cloud provider configs used in fixtures
def azure_config():
    """Azure cloud config fixture."""
    pass


def custom_config():
    """Custom provider config fixture."""
    pass


def hetzner_config():
    """Hetzner cloud config fixture."""
    pass


# Integration test helpers
def mock_aws_session():
    """Helper for mocking AWS session."""
    pass


def mock_azure_client():
    """Helper for mocking Azure client."""
    pass


# Unused variables in test files that are used implicitly
mock_resource = None
error_cloud_service = None
minio_container = None
redis_container = None
rabbitmq_container = None
frame = None
signum = None
Union = None
# Used to patch sys.exit in test_docker_integration.py
sys.exit = None
