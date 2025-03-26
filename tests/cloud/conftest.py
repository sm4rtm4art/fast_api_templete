"""Test fixtures for cloud provider tests."""

import os
from typing import Any, Dict, Union, cast
from unittest.mock import MagicMock, patch

import pytest

from fast_api_template.config.cloud import CloudConfig


class MockSettings:
    """Base mock settings class for all cloud providers."""

    def __init__(self, provider_name: str):
        """Initialize with provider-specific settings."""
        self.provider_name = provider_name
        self._settings = self._get_provider_settings()

    def _get_provider_settings(self) -> Dict[str, Any]:
        """Get provider-specific settings."""
        providers = {
            "aws": {
                "cloud": {
                    "provider": "aws",
                    "region": "us-west-2",
                    "aws": {
                        "profile": None,
                        "s3": {"bucket": "test-bucket"},
                        "sqs": {"queue_url": "https://sqs.us-west-2.amazonaws.com/123456789012/test-queue"},
                        "elasticache": {"endpoint": "test-elasticache.amazonaws.com", "port": 6379},
                    },
                }
            },
            "gcp": {
                "cloud": {
                    "provider": "gcp",
                    "region": "us-central1",
                    "project_id": "test-project",
                    "gcp": {
                        "credentials_path": "/path/to/credentials.json",
                        "storage": {"bucket": "test-bucket", "project_id": "test-project", "type": "gcs"},
                        "pubsub": {
                            "topic": "test-topic",
                            "subscription": "test-subscription",
                            "project_id": "test-project",
                            "type": "pubsub",
                        },
                        "memorystore": {"instance": "test-instance", "type": "memorystore"},
                    },
                }
            },
            "azure": {
                "cloud": {
                    "provider": "azure",
                    "region": "eastus",
                    "tenant_id": "test-tenant-id",
                    "azure": {
                        "subscription_id": "test-subscription-id",
                        "resource_group": "test-resource-group",
                        "connection_string": "DefaultEndpointsProtocol=https;AccountName=teststorage;AccountKey=testkey;EndpointSuffix=core.windows.net",
                        "servicebus_connection_string": "Endpoint=sb://test.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=testkey",
                        "storage": {"container": "test-container", "account_name": "teststorage", "type": "blob"},
                        "servicebus": {"namespace": "test-namespace", "queue": "test-queue", "type": "servicebus"},
                        "redis": {
                            "host": "test-redis.redis.cache.windows.net",
                            "port": 6380,
                            "ssl": True,
                            "type": "azure-redis",
                        },
                    },
                }
            },
            "hetzner": {
                "cloud": {
                    "provider": "hetzner",
                    "region": "eu-central",
                    "hetzner": {
                        "auth_token": "test-token",
                        "object_storage": {
                            "endpoint": "https://s3.eu-central-1.hetzner.com",
                            "access_key": "test-access-key",
                            "secret_key": "test-secret-key",
                            "bucket": "test-bucket",
                            "type": "s3",
                        },
                    },
                }
            },
            "custom": {
                "cloud": {
                    "provider": "custom",
                    "custom_provider_config": {
                        "storage_client_factory": None,
                        "cache_client_factory": None,
                        "queue_client_factory": None,
                        "storage": {
                            "endpoint": "http://localhost:9000",
                            "access_key": "minioadmin",
                            "secret_key": "minioadmin",
                            "bucket": "test-bucket",
                            "type": "s3",
                        },
                        "cache": {"host": "localhost", "port": 6379, "type": "redis"},
                        "queue": {"host": "localhost", "port": 5672, "type": "rabbitmq"},
                    },
                }
            },
            "local": {"cloud": {"provider": "local"}},
        }

        return providers.get(self.provider_name, providers["local"])

    def get(self, key, default=None):
        """Get nested setting by dot-notation key."""
        parts = key.split(".")
        current = self._settings

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def as_dict(self):
        """Return settings as dictionary."""
        return self._settings

    def set(self, key, value):
        """Set nested setting by dot-notation key."""
        parts = key.split(".")
        current = self._settings

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value


@pytest.fixture
def aws_settings():
    """Create mock AWS settings."""
    return MockSettings("aws")


@pytest.fixture
def gcp_settings():
    """Create mock GCP settings."""
    return MockSettings("gcp")


@pytest.fixture
def azure_settings():
    """Create mock Azure settings."""
    return MockSettings("azure")


@pytest.fixture
def hetzner_settings():
    """Create mock Hetzner settings."""
    return MockSettings("hetzner")


@pytest.fixture
def custom_settings():
    """Create mock Custom Provider settings."""
    return MockSettings("custom")


@pytest.fixture
def local_settings():
    """Create mock Local Provider settings."""
    return MockSettings("local")


@pytest.fixture
def aws_config(aws_settings):
    """Create AWS configuration for testing."""
    return CloudConfig(aws_settings)


@pytest.fixture
def gcp_config(gcp_settings):
    """Create GCP configuration for testing."""
    return CloudConfig(gcp_settings)


@pytest.fixture
def azure_config(azure_settings):
    """Create Azure configuration for testing."""
    return CloudConfig(azure_settings)


@pytest.fixture
def hetzner_config(hetzner_settings):
    """Create Hetzner configuration for testing."""
    return CloudConfig(hetzner_settings)


@pytest.fixture
def custom_config(custom_settings):
    """Create Custom Provider configuration for testing."""
    return CloudConfig(custom_settings)


@pytest.fixture
def local_config(local_settings):
    """Create Local Provider configuration for testing."""
    return CloudConfig(local_settings)


# Common mock clients for test assertions
@pytest.fixture
def mock_s3_client():
    """Mock S3 client for AWS tests."""
    client = MagicMock()
    client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
    client.list_objects_v2.return_value = {"Contents": [{"Key": "test-file.txt"}]}
    return client


@pytest.fixture
def mock_sqs_client():
    """Mock SQS client for AWS tests."""
    client = MagicMock()
    client.get_queue_url.return_value = {"QueueUrl": "https://sqs.us-west-2.amazonaws.com/123456789012/test-queue"}
    client.send_message.return_value = {"MessageId": "test-message-id"}
    return client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for cache tests."""
    client = MagicMock()
    client.set.return_value = True
    client.get.return_value = b"cached-data"
    return client


@pytest.fixture
def mock_blob_client():
    """Mock Azure Blob client for tests."""
    client = MagicMock()
    container_client = MagicMock()
    blob_client = MagicMock()
    client.get_container_client.return_value = container_client
    container_client.get_blob_client.return_value = blob_client
    return client


@pytest.fixture
def mock_pubsub_client():
    """Mock GCP Pub/Sub client for tests."""
    publisher = MagicMock()
    publisher.publish.return_value.result.return_value = "test-message-id"
    return publisher


@pytest.fixture
def mock_servicebus_client():
    """Mock Azure ServiceBus client for tests."""
    client = MagicMock()
    sender = MagicMock()
    receiver = MagicMock()
    client.get_queue_sender.return_value = sender
    client.get_queue_receiver.return_value = receiver
    return client


class AzureMockTransport:
    """Mock transport for Azure SDK.

    This transport implementation can be used with any Azure SDK client
    to intercept HTTP requests and return predefined responses without
    making actual network calls.

    Usage:
        from azure.storage.blob import BlobServiceClient
        from azure.core.pipeline.transport import HttpRequest, HttpResponse

        # Create a mock transport that returns a successful response
        mock_transport = AzureMockTransport(responses={
            "container_create": HttpResponse(
                request=HttpRequest("PUT", "https://account.blob.core.windows.net/container"),
                status_code=201,
                headers={"x-ms-request-id": "test-request-id"},
                body=b""
            )
        })

        # Pass the transport to the client
        blob_client = BlobServiceClient(
            account_url="https://account.blob.core.windows.net",
            credential="fake-key",
            transport=mock_transport
        )

        # Now any operations will use the mock transport
        container_client = blob_client.create_container("container")
    """

    def __init__(self, responses=None, status_codes=None, default_status_code=200):
        """Initialize the mock transport.

        Args:
            responses (dict): A dictionary mapping operation names to HttpResponse objects.
            status_codes (dict): A dictionary mapping URL patterns to status codes.
            default_status_code (int): Default status code to return if not specified.
        """
        from azure.core.pipeline.transport import HttpTransport

        self._transport_class = HttpTransport
        self.responses = responses or {}
        self.status_codes = status_codes or {}
        self.default_status_code = default_status_code
        self.requests = []  # Store requests for later inspection

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
        from azure.core.pipeline.transport import HttpResponse

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

        # Create a simple internal response object
        class MockInternalResponse:
            def __init__(self, status, headers, body):
                self.status_code = status
                self.headers = headers
                self.body = body

        internal_response = MockInternalResponse(status=status_code, headers={}, body=b"")

        # Create a new response with proper initialization
        return HttpResponse(request=request, internal_response=internal_response)


class AzureAsyncMockTransport:
    """Async mock transport for Azure SDK.

    This transport implementation can be used with any async Azure SDK client
    to intercept HTTP requests and return predefined responses without
    making actual network calls.

    Usage:
        from azure.storage.blob.aio import BlobServiceClient
        from azure.core.pipeline.transport import HttpRequest, HttpResponse

        # Create a mock transport
        mock_transport = AzureAsyncMockTransport(responses={
            "container_create": HttpResponse(
                request=HttpRequest("PUT", "https://account.blob.core.windows.net/container"),
                status_code=201,
                headers={"x-ms-request-id": "test-request-id"},
                body=b""
            )
        })

        # Pass the transport to the client
        blob_client = BlobServiceClient(
            account_url="https://account.blob.core.windows.net",
            credential="fake-key",
            transport=mock_transport
        )
    """

    def __init__(self, responses=None, status_codes=None, default_status_code=200):
        """Initialize the mock transport.

        Args:
            responses (dict): A dictionary mapping operation names to HttpResponse objects.
            status_codes (dict): A dictionary mapping URL patterns to status codes.
            default_status_code (int): Default status code to return if not specified.
        """
        from azure.core.pipeline.transport import AsyncHttpTransport

        self._transport_class = AsyncHttpTransport
        self.responses = responses or {}
        self.status_codes = status_codes or {}
        self.default_status_code = default_status_code
        self.requests = []  # Store requests for later inspection

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass

    async def send(self, request, **kwargs):
        """Process the request and return a mocked response.

        Args:
            request (HttpRequest): The request object.
            **kwargs: Additional arguments.

        Returns:
            HttpResponse: A mocked HTTP response.
        """
        from azure.core.pipeline.transport import HttpResponse

        # Store the request for later inspection
        self.requests.append((request, kwargs))

        # Check if we have a predefined response for an operation
        operation = kwargs.get("operation_name")
        if operation and operation in self.responses:
            return self.responses[operation]

        # Check if we have a status code for this URL pattern
        status_code = self.default_status_code
        for url_pattern, code in self.status_codes.items():
            if url_pattern in request.url:
                status_code = code
                break

        # Create a simple internal response object
        class MockInternalResponse:
            def __init__(self, status, headers, body):
                self.status_code = status
                self.headers = headers
                self.body = body

        internal_response = MockInternalResponse(
            status=status_code,
            headers={"content-type": "application/json"},
            body=kwargs.get("body", b'{"status": "mocked"}'),
        )

        # Create and return a response
        response = HttpResponse(request=request, internal_response=internal_response)
        response.status_code = status_code  # Ensure status code is set correctly
        return response


@pytest.fixture
def cloud_test_env():
    """Creates a test environment with various Docker containers for integrated testing.

    This fixture sets up:
    - A MinIO container for S3-compatible storage testing
    - A Redis container for cache testing
    - A RabbitMQ container for message queue testing

    After the tests, it cleans up all containers.
    """
    # Store original environment variables
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


@pytest.fixture
def mock_boto3():
    """Create a mock for boto3."""
    mock = MagicMock()

    # Mock S3 client
    mock_s3 = MagicMock()
    mock.client.return_value = mock_s3

    # Mock resource
    mock_resource = MagicMock()
    mock.resource.return_value = mock_resource

    return mock


@pytest.fixture
def mock_gcp_storage():
    """Create a mock for Google Cloud Storage."""
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_client.bucket.return_value = mock_bucket

    return mock_client


@pytest.fixture
def mock_azure_blob():
    """Create a mock for Azure Blob Storage."""
    mock_client = MagicMock()

    return mock_client


@pytest.fixture
def mock_redis():
    """Create a mock for Redis client."""
    mock_client = MagicMock()

    return mock_client


@pytest.fixture
def mock_rabbitmq():
    """Create a mock for RabbitMQ client."""
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel

    return {"connection": mock_connection, "channel": mock_channel}
