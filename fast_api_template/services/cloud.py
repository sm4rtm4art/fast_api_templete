"""Cloud service implementations for different providers."""

from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Union

import boto3
from azure.storage.blob import BlobServiceClient
from botocore.client import BaseClient
from google.cloud import pubsub_v1, storage
from redis import Redis

from fast_api_template.config.cloud import CloudConfig

# Define a generic type for cloud clients
CloudClient = TypeVar(
    "CloudClient",
    bound=Union[BaseClient, storage.Client, BlobServiceClient, Redis],
)

# Define allowed AWS service names
AWSServiceName = Any  # Use Any since boto3's type hints are too specific


class CloudService(ABC):
    """Abstract base class for cloud services."""

    def __init__(self, config: CloudConfig):
        self.config = config

    @abstractmethod
    def get_client(self) -> Optional[CloudClient]:
        """Get the cloud service client."""
        pass


class StorageService(CloudService):
    """Cloud storage service implementation."""

    def get_client(  # type: ignore[override]
        self,
    ) -> Optional[Union[BaseClient, storage.Client, BlobServiceClient]]:
        """Get the appropriate storage client based on provider."""
        storage_config = self.config.get_storage_config()

        if storage_config["type"] == "s3":
            service_name: AWSServiceName = "s3"
            return boto3.client(  # type: ignore[call-overload]
                service_name=service_name,
                region_name=storage_config["region"],
                profile_name=(self.config.aws_config["profile"] if self.config.aws_config else None),
            )
        elif storage_config["type"] == "gcs":
            return storage.Client(
                project=storage_config["project_id"],
                credentials=(self.config.gcp_config["credentials_path"] if self.config.gcp_config else None),
            )
        elif storage_config["type"] == "azure":
            connection_string = self.config.azure_config["connection_string"] if self.config.azure_config else None
            if connection_string is None:
                return None
            return BlobServiceClient.from_connection_string(connection_string)
        return None


class CacheService(CloudService):
    """Cloud cache service implementation."""

    def get_client(  # type: ignore[override]
        self,
    ) -> Optional[Redis]:
        """Get the appropriate cache client based on provider."""
        cache_config = self.config.get_cache_config()

        if cache_config["type"] == "elasticache":
            return Redis(
                host=cache_config["endpoint"],
                port=cache_config["port"],
                decode_responses=True,
            )
        elif cache_config["type"] == "memorystore":
            return Redis(
                host=cache_config["instance"],
                port=6379,
                decode_responses=True,
            )
        return None


class QueueService(CloudService):
    """Cloud queue service implementation."""

    def get_client(  # type: ignore[override]
        self,
    ) -> Optional[Union[BaseClient, pubsub_v1.PublisherClient]]:
        """Get the appropriate queue client based on provider."""
        queue_config = self.config.get_queue_config()

        if queue_config["type"] == "sqs":
            service_name: AWSServiceName = "sqs"
            return boto3.client(  # type: ignore[call-overload]
                service_name=service_name,
                region_name=queue_config["region"],
                profile_name=(self.config.aws_config["profile"] if self.config.aws_config else None),
            )
        elif queue_config["type"] == "pubsub":
            return pubsub_v1.PublisherClient()
        return None


class CloudServiceFactory:
    """Factory for creating cloud services."""

    @staticmethod
    def create_storage_service(config: CloudConfig) -> StorageService:
        """Create a storage service instance."""
        return StorageService(config)

    @staticmethod
    def create_cache_service(config: CloudConfig) -> CacheService:
        """Create a cache service instance."""
        return CacheService(config)

    @staticmethod
    def create_queue_service(config: CloudConfig) -> QueueService:
        """Create a queue service instance."""
        return QueueService(config)
