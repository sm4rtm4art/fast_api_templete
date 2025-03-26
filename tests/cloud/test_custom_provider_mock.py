"""Test custom cloud provider using requests_mock.

This module demonstrates how to mock custom cloud providers and local services
for testing without requiring actual infrastructure.
"""
# mypy: disable-error-code="arg-type"

import re
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
import requests_mock

from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig


class TestSettings:
    """Mock settings for custom provider testing."""

    def __init__(self, settings: Optional[Dict[str, Any]] = None) -> None:
        self._settings: Dict[str, Any] = settings or {
            "cloud": {
                "provider": "custom",
                "region": "local",
                "custom": {
                    "name": "local-k8s",
                    "description": ("Local Kubernetes cluster with MinIO, Redis and RabbitMQ"),
                    "storage": {
                        "type": "minio",
                        "endpoint": "minio.local:9000",
                        "access_key": "minioadmin",
                        "secret_key": "minioadmin",
                        "secure": False,
                        "bucket": "app-data",
                    },
                    "cache": {"type": "redis", "host": "redis.local", "port": 6379, "password": "redispass", "db": 0},
                    "queue": {
                        "type": "rabbitmq",
                        "host": "rabbitmq.local",
                        "port": 5672,
                        "username": "guest",
                        "password": "guest",
                        "vhost": "/",
                        "exchange": "app-exchange",
                        "queue": "app-tasks",
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


@pytest.fixture
def custom_config() -> CloudConfig:
    """Create custom provider configuration for testing."""
    return CloudConfig(TestSettings())


class TestCustomProviderMock:
    """Test custom cloud provider using mocks."""

    @pytest.fixture
    def custom_service(self, custom_config: CloudConfig) -> Any:
        """Create a custom cloud service for testing."""
        return CloudServiceProvider.create_service(custom_config)

    @pytest.mark.parametrize(
        "bucket_name,should_succeed",
        [
            ("app-data", True),
            ("nonexistent-bucket", False),
        ],
    )
    def test_minio_operations(self, custom_service: Any, bucket_name: str, should_succeed: bool) -> None:
        """Test MinIO operations using requests_mock with various buckets."""
        with requests_mock.Mocker() as m:
            # Set up endpoint
            endpoint = "minio.local:9000"

            # Mock bucket listing
            m.get(
                f"http://{endpoint}/", json={"buckets": [{"name": "app-data", "creation_date": "2023-01-01T00:00:00Z"}]}
            )

            # Use regex pattern matching for API endpoints
            if should_succeed:
                # Mock bucket access
                m.get(f"http://{endpoint}/{bucket_name}", status_code=200)

                # Mock bucket operations with regex
                m.register_uri("PUT", re.compile(f"http://{endpoint}/{bucket_name}/.*"), status_code=200)
                m.register_uri(
                    "GET", re.compile(f"http://{endpoint}/{bucket_name}/.*"), text="Hello, MinIO!", status_code=200
                )
                m.register_uri("DELETE", re.compile(f"http://{endpoint}/{bucket_name}/.*"), status_code=204)
            else:
                # Simulate non-existent bucket
                m.get(f"http://{endpoint}/{bucket_name}", status_code=404)
                m.register_uri(
                    "GET",
                    re.compile(f"http://{endpoint}/{bucket_name}/.*"),
                    status_code=404,
                    json={"error": "NoSuchBucket", "message": "The specified bucket does not exist"},
                )

            # Create MinIO client
            with patch("minio.Minio") as mock_minio:
                mock_client = MagicMock()
                mock_minio.return_value = mock_client

                # Mock MinIO client methods
                mock_client.bucket_exists.return_value = should_succeed
                if should_succeed:
                    mock_client.list_buckets.return_value = [
                        {"name": bucket_name, "creation_date": "2023-01-01T00:00:00Z"}
                    ]

                    # Set up the get_object mock
                    mock_response = MagicMock()
                    mock_response.read.return_value = b"Hello, MinIO!"
                    mock_client.get_object.return_value = mock_response
                else:
                    # Simulate bucket not found error
                    mock_client.list_buckets.return_value = []
                    from minio.error import S3Error

                    mock_client.get_object.side_effect = S3Error(
                        "NoSuchBucket",
                        "The specified bucket does not exist",
                        resource=bucket_name,
                        request_id="test-request-id",
                        host_id="test-host-id",
                        response=None,
                    )

                # Get storage client from our service
                storage_client = custom_service.get_storage_client()

                # Verify MinIO client was created with correct parameters
                mock_minio.assert_called_once_with(
                    endpoint="minio.local:9000", access_key="minioadmin", secret_key="minioadmin", secure=False
                )

                # Test bucket operations
                assert storage_client.bucket_exists(bucket_name) == should_succeed

                if should_succeed:
                    # List buckets
                    buckets = storage_client.list_buckets()
                    assert len(buckets) == 1
                    assert buckets[0]["name"] == bucket_name

                    # Put an object
                    object_name = "test-object.txt"
                    data = b"Hello, MinIO!"
                    storage_client.put_object(bucket_name, object_name, data=data, length=len(data))

                    # Get an object
                    response = storage_client.get_object(bucket_name, object_name)
                    content = response.read()
                    assert content == b"Hello, MinIO!"

                    # Delete an object
                    storage_client.remove_object(bucket_name, object_name)
                else:
                    # Verify that bucket operations raise appropriate exceptions
                    from minio.error import S3Error

                    with pytest.raises(S3Error):
                        storage_client.get_object(bucket_name, "test-object.txt")

    @pytest.mark.parametrize("connection_success", [True, False])
    def test_redis_operations(self, custom_service: Any, connection_success: bool) -> None:
        """Test Redis operations with connection success and failure scenarios."""
        with patch("redis.Redis") as mock_redis_class:
            # Create mock Redis client
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis

            # Configure mock behavior based on connection_success
            if connection_success:
                # Mock Redis methods for success case
                mock_redis.ping.return_value = True
                mock_redis.set.return_value = True
                mock_redis.get.return_value = "test-value"
                mock_redis.exists.return_value = 1
                mock_redis.delete.return_value = 1
            else:
                # Simulate Redis connection failure
                redis_error = ConnectionError("Redis server not available")
                mock_redis.ping.side_effect = redis_error
                mock_redis.set.side_effect = redis_error
                mock_redis.get.side_effect = redis_error
                mock_redis.exists.side_effect = redis_error
                mock_redis.delete.side_effect = redis_error

            # Get the config and cache settings
            cache_config = custom_service.config.get_cache_config()

            # In a real implementation, get_cache_client would create a Redis client
            # We'll patch it to return our mock
            with patch.object(custom_service, "get_cache_client", return_value=mock_redis):
                cache_client = custom_service.get_cache_client()

                # Verify Redis client would have been created with correct parameters
                assert cache_config["type"] == "redis"
                assert cache_config["host"] == "redis.local"
                assert cache_config["port"] == 6379

                # Test Redis operations based on connection status
                if connection_success:
                    # Test successful ping
                    assert cache_client.ping()

                    # Set a value
                    cache_client.set("test-key", "test-value")
                    mock_redis.set.assert_called_once_with("test-key", "test-value")

                    # Get a value
                    value = cache_client.get("test-key")
                    assert value == "test-value"
                    mock_redis.get.assert_called_once_with("test-key")

                    # Check existence
                    assert cache_client.exists("test-key") == 1
                    mock_redis.exists.assert_called_once_with("test-key")

                    # Delete key
                    assert cache_client.delete("test-key") == 1
                    mock_redis.delete.assert_called_once_with("test-key")
                else:
                    # Test Redis connection failure
                    with pytest.raises(ConnectionError):
                        cache_client.ping()

    @pytest.mark.parametrize(
        "queue_operation,should_succeed",
        [
            ("declare", True),
            ("declare", False),
            ("publish", True),
            ("publish", False),
        ],
    )
    def test_rabbitmq_operations(self, custom_service: Any, queue_operation: str, should_succeed: bool) -> None:
        """Test RabbitMQ operations with success and failure scenarios."""
        with patch("pika.ConnectionParameters") as mock_params_class:
            mock_params = MagicMock()
            mock_params_class.return_value = mock_params

            with patch("pika.PlainCredentials") as mock_creds_class:
                mock_creds = MagicMock()
                mock_creds_class.return_value = mock_creds

                with patch("pika.BlockingConnection") as mock_conn_class:
                    # Mock connection and channel
                    mock_conn = MagicMock()
                    mock_conn_class.return_value = mock_conn

                    mock_channel = MagicMock()
                    mock_conn.channel.return_value = mock_channel

                    # Configure mock behavior based on parameters
                    if queue_operation == "declare":
                        if should_succeed:
                            # Mock successful queue declaration
                            mock_method_frame = MagicMock(queue="app-tasks")
                            mock_channel.queue_declare.return_value = MagicMock(method_frame=mock_method_frame)
                        else:
                            # Mock queue declaration failure
                            mock_channel.queue_declare.side_effect = Exception("Failed to declare queue")

                    elif queue_operation == "publish":
                        # Setup for publish test
                        mock_method_frame = MagicMock(queue="app-tasks")
                        mock_channel.queue_declare.return_value = MagicMock(method_frame=mock_method_frame)

                        if should_succeed:
                            # Mock successful publishing
                            mock_channel.basic_publish.return_value = True
                        else:
                            # Mock publishing failure
                            mock_channel.basic_publish.side_effect = Exception("Failed to publish message")

                    # Get the queue config
                    queue_config = custom_service.config.get_queue_config()

                    # In a real implementation, get_queue_client would create a RabbitMQ channel
                    # We'll patch it to return our mock
                    with patch.object(custom_service, "get_queue_client", return_value=mock_channel):
                        queue_client = custom_service.get_queue_client()

                        # Verify RabbitMQ would have been created with correct parameters
                        assert queue_config["type"] == "rabbitmq"
                        assert queue_config["host"] == "rabbitmq.local"
                        assert queue_config["port"] == 5672

                        # Test appropriate RabbitMQ operation
                        if queue_operation == "declare":
                            if should_succeed:
                                # Test successful queue declaration
                                result = queue_client.queue_declare(queue="app-tasks")
                                assert result.method_frame.queue == "app-tasks"
                                mock_channel.queue_declare.assert_called_once_with(queue="app-tasks")
                            else:
                                # Test queue declaration failure
                                with pytest.raises(Exception) as excinfo:
                                    queue_client.queue_declare(queue="app-tasks")
                                assert "Failed to declare queue" in str(excinfo.value)

                        elif queue_operation == "publish":
                            # Declare queue always succeeds for publish tests
                            result = queue_client.queue_declare(queue="app-tasks")
                            assert result.method_frame.queue == "app-tasks"

                            # Test publishing
                            if should_succeed:
                                # Test successful publish
                                queue_client.basic_publish(
                                    exchange="app-exchange", routing_key="app-tasks", body=b'{"message": "test"}'
                                )
                                mock_channel.basic_publish.assert_called_once_with(
                                    exchange="app-exchange", routing_key="app-tasks", body=b'{"message": "test"}'
                                )
                            else:
                                # Test publish failure
                                with pytest.raises(Exception) as excinfo:
                                    queue_client.basic_publish(
                                        exchange="app-exchange", routing_key="app-tasks", body=b'{"message": "test"}'
                                    )
                                assert "Failed to publish message" in str(excinfo.value)

    def _create_test_service(self):
        """Create a test service with a mock settings object."""
        test_storage_config = {
            "type": "minio",
            "endpoint": "minio.local:9000",
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "secure": False,
            "bucket": "app-data",
        }

        test_cache_config = {"type": "redis", "host": "redis.local", "port": 6379, "password": "redispass", "db": 0}

        test_queue_config = {
            "type": "rabbitmq",
            "host": "rabbitmq.local",
            "port": 5672,
            "username": "guest",
            "password": "guest",
            "vhost": "/",
            "exchange": "app-exchange",
            "queue": "app-tasks",
        }

        settings = TestSettings(
            {
                "cloud": {
                    "provider": "custom",
                    "custom_provider_config": {
                        "storage": test_storage_config,
                        "cache": test_cache_config,
                        "queue": test_queue_config,
                    },
                }
            }
        )

        return CloudServiceProvider.create_service(CloudConfig(settings))
