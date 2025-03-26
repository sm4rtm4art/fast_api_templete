"""Custom cloud service implementation.

This module provides a custom cloud service that can be configured to use
any storage, cache, or queue provider.
"""

from typing import Any, Optional

from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.config.cloud import CloudConfig


class CustomCloudService(CloudService):
    """Custom cloud service provider implementation.

    This class allows for using any storage, cache, or queue service
    by configuring them in settings or providing custom factory functions.
    """

    def __init__(self, config: CloudConfig):
        """Initialize with cloud configuration.

        Args:
            config: The cloud configuration object
        """
        self.config = config
        # Support both the new property name (custom_config) and
        # the old one (custom_provider_config) for backward compatibility
        self.custom_config = getattr(config, "custom_config", {})
        self.custom_provider_config = getattr(config, "custom_provider_config", self.custom_config)

        # Try to get service configs from both regular config and custom config
        self.storage_config = config.get_storage_config() or self.custom_provider_config.get("storage", {})
        self.cache_config = config.get_cache_config() or self.custom_provider_config.get("cache", {})
        self.queue_config = config.get_queue_config() or self.custom_provider_config.get("queue", {})

    def get_storage_client(self) -> Optional[Any]:
        """Get a storage client based on configuration.

        Returns:
            A storage client instance or None if not configured
        """
        if not self.storage_config:
            return None

        # Check if there's a custom factory function (in either property)
        factory = self.custom_config.get("storage_client_factory") or self.custom_provider_config.get(
            "storage_client_factory"
        )
        if factory and callable(factory):
            return factory(self.storage_config)

        # Default implementations based on type
        storage_type = self.storage_config.get("type", "")

        if storage_type == "s3" or storage_type == "minio":
            try:
                import minio

                return minio.Minio(
                    endpoint=self.storage_config.get("endpoint", "localhost:9000"),
                    access_key=self.storage_config.get("access_key", "minioadmin"),
                    secret_key=self.storage_config.get("secret_key", "minioadmin"),
                    secure=self.storage_config.get("secure", False),
                )
            except ImportError:
                return None

        return None

    def get_cache_client(self) -> Optional[Any]:
        """Get a cache client based on configuration.

        Returns:
            A cache client instance or None if not configured
        """
        if not self.cache_config:
            return None

        # Check if there's a custom factory function (in either property)
        factory = self.custom_config.get("cache_client_factory") or self.custom_provider_config.get(
            "cache_client_factory"
        )
        if factory and callable(factory):
            return factory(self.cache_config)

        # Default implementations based on type
        cache_type = self.cache_config.get("type", "")

        if cache_type == "redis":
            try:
                import redis

                return redis.Redis(
                    host=self.cache_config.get("host", "localhost"),
                    port=self.cache_config.get("port", 6379),
                    db=self.cache_config.get("db", 0),
                    password=self.cache_config.get("password", None),
                    decode_responses=True,
                )
            except ImportError:
                return None

        return None

    def get_queue_client(self) -> Optional[Any]:
        """Get a queue client based on configuration.

        Returns:
            A queue client instance or None if not configured
        """
        if not self.queue_config:
            return None

        # Check if there's a custom factory function (in either property)
        factory = self.custom_config.get("queue_client_factory") or self.custom_provider_config.get(
            "queue_client_factory"
        )
        if factory and callable(factory):
            return factory(self.queue_config)

        # Default implementations based on type
        queue_type = self.queue_config.get("type", "")

        if queue_type == "rabbitmq":
            try:
                import pika

                credentials = pika.PlainCredentials(  # type: ignore
                    username=self.queue_config.get("username", "guest"),
                    password=self.queue_config.get("password", "guest"),
                )
                connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=self.queue_config.get("host", "localhost"),
                        port=self.queue_config.get("port", 5672),
                        credentials=credentials,
                    )
                )
                return connection.channel()
            except ImportError:
                return None

        return None
