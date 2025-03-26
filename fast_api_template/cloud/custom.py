"""Custom cloud service implementation."""

from typing import Any, Optional

from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.config.cloud import CloudConfig


class CustomCloudService(CloudService):
    """Implementation of CloudService for custom cloud providers.

    This implementation allows for flexible configuration of any cloud provider
    that is not directly supported out of the box. It can be used for
    on-premise solutions, custom Kubernetes clusters, or any other infrastructure.
    """

    def __init__(self, config: CloudConfig):
        """Initialize the custom cloud service with configuration.

        Args:
            config: Cloud configuration containing custom provider settings
        """
        super().__init__(config)
        self.custom_config = config.custom_provider_config or {}
        self._storage_client_factory = self.custom_config.get("storage_client_factory")
        self._cache_client_factory = self.custom_config.get("cache_client_factory")
        self._queue_client_factory = self.custom_config.get("queue_client_factory")

        # Storage configuration
        self.storage_config = self.custom_config.get("storage", {})

        # Cache configuration
        self.cache_config = self.custom_config.get("cache", {})

        # Queue configuration
        self.queue_config = self.custom_config.get("queue", {})

    def get_storage_client(self) -> Optional[Any]:
        """Get the storage client for custom storage service.

        Returns:
            A client object for interacting with the custom storage service
            or None if not configured
        """
        if callable(self._storage_client_factory):
            return self._storage_client_factory(self.storage_config)

        # Default implementation for common storage types
        storage_type = self.storage_config.get("type")

        if storage_type == "minio":
            # MinIO is a common self-hosted S3-compatible service
            try:
                from minio import Minio

                return Minio(
                    endpoint=self.storage_config.get("endpoint", "localhost:9000"),
                    access_key=self.storage_config.get("access_key", ""),
                    secret_key=self.storage_config.get("secret_key", ""),
                    secure=self.storage_config.get("secure", False),
                )
            except ImportError:
                return None

        return None

    def get_cache_client(self) -> Optional[Any]:
        """Get the cache client for custom cache service.

        Returns:
            A client object for interacting with the custom cache service
            or None if not configured
        """
        if callable(self._cache_client_factory):
            return self._cache_client_factory(self.cache_config)

        # Default implementation for common cache types
        cache_type = self.cache_config.get("type")

        if cache_type == "redis":
            try:
                from redis import Redis

                return Redis(
                    host=self.cache_config.get("host", "localhost"),
                    port=self.cache_config.get("port", 6379),
                    password=self.cache_config.get("password"),
                    db=self.cache_config.get("db", 0),
                    decode_responses=True,
                )
            except ImportError:
                return None

        return None

    def get_queue_client(self) -> Optional[Any]:
        """Get the queue client for custom message queue service.

        Returns:
            A client object for interacting with the custom message queue
            or None if not configured
        """
        if callable(self._queue_client_factory):
            return self._queue_client_factory(self.queue_config)

        # Default implementation for common queue types
        queue_type = self.queue_config.get("type")

        if queue_type == "rabbitmq":
            try:
                import pika

                credentials = pika.PlainCredentials(
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
