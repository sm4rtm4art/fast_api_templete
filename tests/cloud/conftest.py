"""Common test fixtures for cloud service tests.

This module contains shared fixtures and mock classes used across
cloud service provider tests.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

import boto3
import pytest
from moto import mock_aws

from fast_api_template.config.cloud import CloudConfig


class MockSettings:
    """Mock settings for cloud testing.

    This class implements the SettingsProtocol interface for testing.
    We use a different name than TestSettings to avoid pytest trying
    to collect it as a test class.
    """

    def __init__(self) -> None:
        self._settings: Dict[str, Any] = {
            "cloud": {
                "provider": "aws",
                "region": "us-west-2",
                "aws": {
                    "profile": None,  # No profile for Moto
                    "s3": {"bucket": "test-bucket"},
                    "sqs": {
                        "queue_url": None  # Will be set during test
                    },
                },
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get nested setting by dot-notation key."""
        parts = key.split(".")
        current = self._settings

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def as_dict(self) -> Dict[str, Any]:
        """Return settings as dictionary."""
        return self._settings

    def set(self, key: str, value: Any) -> None:
        """Set nested setting by dot-notation key."""
        parts = key.split(".")
        current = self._settings

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    def copy(self) -> "MockSettings":
        """Create a copy of the settings object."""
        new_settings = MockSettings()
        new_settings._settings = {
            key: value.copy() if isinstance(value, dict) else value for key, value in self._settings.items()
        }
        return new_settings


class AzureMockTransport:
    """Mock transport for Azure SDK.

    This transport implementation can be used with any Azure SDK client
    to intercept HTTP requests and return predefined responses without
    making actual network calls.
    """

    def __init__(
        self,
        responses: Optional[Dict[str, Any]] = None,
        status_codes: Optional[Dict[str, int]] = None,
        default_status_code: int = 200,
    ) -> None:
        """Initialize the mock transport.

        Args:
            responses: A dictionary mapping operation names to HttpResponse objects.
            status_codes: A dictionary mapping URL patterns to status codes.
            default_status_code: Default status code to return if not specified.
        """
        self.responses = responses or {}
        self.status_codes = status_codes or {}
        self.default_status_code = default_status_code
        self.requests: List[Tuple[Any, Dict[str, Any]]] = []  # Store requests for later inspection

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send(self, request, **kwargs):
        """Send a request and return a mocked response.

        Args:
            request: The HTTP request object
            **kwargs: Additional keyword arguments

        Returns:
            HttpResponse: A mocked response object
        """

        # Create a simple mock response
        class MockResponse:
            def __init__(self, status_code, headers, body):
                self.status_code = status_code
                self.headers = headers
                self.body = body
                self.request = request

        # Store request for later verification
        self.requests.append((request, kwargs))

        # Check if we have a pre-defined response for this request
        for name, response in self.responses.items():
            if hasattr(response, "request") and response.request and response.request.url in request.url:
                return response

        # Otherwise create a default response based on URL mapping
        status_code = self.default_status_code
        for pattern, code in self.status_codes.items():
            if pattern in request.url:
                status_code = code
                break

        # Create a new response
        return MockResponse(status_code=status_code, headers={}, body=b"")


@pytest.fixture
def aws_settings() -> MockSettings:
    """Create mock settings for AWS tests."""
    return MockSettings()


@pytest.fixture
def aws_config(aws_settings: MockSettings) -> CloudConfig:
    """Create AWS configuration for testing."""
    return CloudConfig(aws_settings)  # type: ignore


@pytest.fixture
def aws_config_with_sqs_queue(aws_settings: MockSettings) -> CloudConfig:
    """Return a modified AWS config with SQS queue URL set."""
    # Create a copy of the settings
    settings = aws_settings.copy()

    # Create a test queue
    with mock_aws():
        sqs_client = boto3.client("sqs", region_name="us-west-2")
        response = sqs_client.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]

    # Set the queue URL in the settings
    settings.set("cloud.aws.sqs.queue_url", queue_url)

    return CloudConfig(settings)  # type: ignore


@pytest.fixture
def gcp_settings() -> MockSettings:
    """Create mock GCP settings."""
    return MockSettings()


@pytest.fixture
def gcp_config(gcp_settings: MockSettings) -> CloudConfig:
    """Create GCP configuration for testing."""
    return CloudConfig(gcp_settings)  # type: ignore


@pytest.fixture
def azure_settings() -> MockSettings:
    """Create mock Azure settings."""
    return MockSettings()


@pytest.fixture
def azure_config(azure_settings: MockSettings) -> CloudConfig:
    """Create Azure configuration for testing."""
    return CloudConfig(azure_settings)  # type: ignore


@pytest.fixture
def hetzner_settings() -> MockSettings:
    """Create mock Hetzner settings."""
    return MockSettings()


@pytest.fixture
def hetzner_config(hetzner_settings: MockSettings) -> CloudConfig:
    """Create Hetzner configuration for testing."""
    return CloudConfig(hetzner_settings)  # type: ignore


@pytest.fixture
def custom_settings() -> MockSettings:
    """Create mock Custom Provider settings."""
    return MockSettings()


@pytest.fixture
def custom_config(custom_settings: MockSettings) -> CloudConfig:
    """Create Custom Provider configuration for testing."""
    return CloudConfig(custom_settings)  # type: ignore


@pytest.fixture
def local_settings() -> MockSettings:
    """Create mock Local Provider settings."""
    return MockSettings()


@pytest.fixture
def local_config(local_settings: MockSettings) -> CloudConfig:
    """Create Local Provider configuration for testing."""
    return CloudConfig(local_settings)  # type: ignore


@pytest.fixture
def cloud_test_env():
    """Creates a test environment with environment variables for cloud testing.

    This fixture sets up environment variables needed for cloud integration
    testing and cleans them up afterward.
    """
    # Store original environment variables
    import os

    original_env = {}
    test_env_vars = {
        "AWS_ACCESS_KEY_ID": "test-access-key",
        "AWS_SECRET_ACCESS_KEY": "test-secret-key",
        "AWS_DEFAULT_REGION": "us-west-2",
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/test-credentials.json",
        "AZURE_TENANT_ID": "test-tenant",
        "AZURE_SUBSCRIPTION_ID": "test-subscription",
        "AZURE_CLIENT_ID": "test-client",
        "AZURE_CLIENT_SECRET": "test-secret",
        "HETZNER_API_TOKEN": "test-api-token",
        "MINIO_ACCESS_KEY": "minioadmin",
        "MINIO_SECRET_KEY": "minioadmin",
    }

    # Set environment variables for testing
    for key, value in test_env_vars.items():
        if key in os.environ:
            original_env[key] = os.environ[key]
        os.environ[key] = value

    yield test_env_vars

    # Restore original environment
    for key in test_env_vars:
        if key in original_env:
            os.environ[key] = original_env[key]
        else:
            del os.environ[key]
