"""Test custom cloud service implementation."""

from unittest.mock import MagicMock, patch

import pytest

from fast_api_template.cloud.custom import CustomCloudService
from fast_api_template.config.cloud import CloudConfig


class TestCustomCloudService:
    """Test suite for custom cloud service."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for custom provider."""
        config = MagicMock(spec=CloudConfig)
        config.provider = "custom"

        # Set up the storage, cache, and queue configs
        storage_config = {
            "type": "minio",
            "endpoint": "minio.example.com:9000",
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "secure": True,
        }

        cache_config = {"type": "redis", "host": "redis.example.com", "port": 6379, "password": "redispass"}

        queue_config = {
            "type": "rabbitmq",
            "host": "rabbitmq.example.com",
            "port": 5672,
            "username": "guest",
            "password": "guest",
        }

        # Mock the custom_provider_config property
        custom_config = {
            "storage": storage_config,
            "cache": cache_config,
            "queue": queue_config,
        }
        config.custom_provider_config = custom_config

        # Add the get_storage_config method
        config.get_storage_config.return_value = storage_config
        config.get_cache_config.return_value = cache_config
        config.get_queue_config.return_value = queue_config

        return config

    @patch("minio.Minio")
    def test_get_storage_client_minio(self, mock_minio, mock_config):
        """Test getting MinIO storage client."""
        # Setup
        mock_minio_instance = MagicMock()
        mock_minio.return_value = mock_minio_instance

        # Execute
        service = CustomCloudService(mock_config)
        client = service.get_storage_client()

        # Verify
        assert client is mock_minio_instance
        mock_minio.assert_called_once_with(
            endpoint="minio.example.com:9000", access_key="minioadmin", secret_key="minioadmin", secure=True
        )

    @patch("minio.Minio", side_effect=ImportError)
    def test_get_storage_client_import_error(self, mock_minio, mock_config):
        """Test handling ImportError for storage client."""
        # Execute
        service = CustomCloudService(mock_config)
        client = service.get_storage_client()

        # Verify
        assert client is None

    def test_get_storage_client_custom_factory(self, mock_config):
        """Test getting storage client with custom factory."""
        # Setup
        mock_factory = MagicMock()
        mock_storage_client = MagicMock()
        mock_factory.return_value = mock_storage_client

        custom_config = mock_config.custom_provider_config
        custom_config["storage_client_factory"] = mock_factory

        # Execute
        service = CustomCloudService(mock_config)
        client = service.get_storage_client()

        # Verify
        assert client is mock_storage_client
        mock_factory.assert_called_once_with(custom_config["storage"])

    @patch("redis.Redis")
    def test_get_cache_client_redis(self, mock_redis, mock_config):
        """Test getting Redis cache client."""
        # Setup
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        # Execute
        service = CustomCloudService(mock_config)
        client = service.get_cache_client()

        # Verify
        assert client is mock_redis_instance
        mock_redis.assert_called_once_with(
            host="redis.example.com", port=6379, password="redispass", db=0, decode_responses=True
        )

    @patch("pika.BlockingConnection")
    @patch("pika.ConnectionParameters")
    @patch("pika.PlainCredentials")
    def test_get_queue_client_rabbitmq(self, mock_credentials, mock_params, mock_connection, mock_config):
        """Test getting RabbitMQ queue client."""
        # Setup
        mock_channel = MagicMock()
        mock_connection_instance = MagicMock()
        mock_connection_instance.channel.return_value = mock_channel
        mock_connection.return_value = mock_connection_instance

        mock_params_instance = MagicMock()
        mock_params.return_value = mock_params_instance

        mock_credentials_instance = MagicMock()
        mock_credentials.return_value = mock_credentials_instance

        # Execute
        service = CustomCloudService(mock_config)
        client = service.get_queue_client()

        # Verify
        assert client is mock_channel
        mock_credentials.assert_called_once_with(username="guest", password="guest")
        mock_params.assert_called_once_with(
            host="rabbitmq.example.com", port=5672, credentials=mock_credentials_instance
        )
        mock_connection.assert_called_once_with(mock_params_instance)
        mock_connection_instance.channel.assert_called_once()
