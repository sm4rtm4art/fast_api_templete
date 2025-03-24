"""Cloud service interface definitions."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from fast_api_template.config.cloud import CloudConfig


class CloudService(ABC):
    """Abstract base class for cloud service operations.

    This interface defines the contract that all cloud service implementations
    must follow. It provides methods for accessing storage, cache, and queue
    services across different cloud providers.
    """

    def __init__(self, config: CloudConfig):
        """Initialize the cloud service with configuration.

        Args:
            config: Cloud configuration containing provider-specific settings
        """
        self.config = config

    @abstractmethod
    def get_storage_client(self) -> Optional[Any]:
        """Get the storage client for file/blob storage operations.

        Returns:
            A client object for interacting with the cloud storage service
            (e.g., S3, GCS, Blob Storage) or None if not configured
        """
        pass

    @abstractmethod
    def get_cache_client(self) -> Optional[Any]:
        """Get the cache client for key-value storage operations.

        Returns:
            A client object for interacting with the cloud cache service
            (e.g., ElastiCache, Memorystore, Redis Cache) or None if not configured
        """
        pass

    @abstractmethod
    def get_queue_client(self) -> Optional[Any]:
        """Get the queue client for message queue operations.

        Returns:
            A client object for interacting with the cloud queue service
            (e.g., SQS, Pub/Sub, Service Bus) or None if not configured
        """
        pass
