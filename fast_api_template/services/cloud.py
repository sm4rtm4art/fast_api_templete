"""Cloud service implementations for different providers."""

from abc import ABC, abstractmethod
from typing import Optional, TypeVar, cast

import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import pubsub_v1, storage
from redis import Redis

from fast_api_template.config.cloud import CloudConfig

# Define type for cloud clients
CloudClient = TypeVar("CloudClient", covariant=True)


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

    def get_client(
        self,
    ) -> Optional[CloudClient]:
        """Get the appropriate storage client based on provider."""
        storage_config = self.config.get_storage_config()

        if storage_config["type"] == "s3":
            return cast(
                CloudClient,
                boto3.client(  # type: ignore
                    service_name="s3",
                    region_name=storage_config.get("region", "us-east-1"),
                    profile_name=(self.config.aws_config.get("profile") if self.config.aws_config else None),
                ),
            )
        elif storage_config["type"] == "gcs":
            return cast(
                CloudClient,
                storage.Client(
                    project=storage_config["project_id"],
                    credentials=(self.config.gcp_config.get("credentials_path") if self.config.gcp_config else None),
                ),
            )
        elif storage_config["type"] == "azure":
            connection_string = self.config.azure_config.get("connection_string") if self.config.azure_config else None
            if connection_string is None:
                return None
            return cast(CloudClient, BlobServiceClient.from_connection_string(connection_string))
        return None


class CacheService(CloudService):
    """Cloud cache service implementation."""

    def get_client(
        self,
    ) -> Optional[CloudClient]:
        """Get the appropriate cache client based on provider."""
        cache_config = self.config.get_cache_config()

        if cache_config["type"] == "elasticache":
            return cast(
                CloudClient,
                Redis(
                    host=cache_config["endpoint"],
                    port=cache_config["port"],
                    decode_responses=True,
                ),
            )
        elif cache_config["type"] == "memorystore":
            return cast(
                CloudClient,
                Redis(
                    host=cache_config["instance"],
                    port=6379,
                    decode_responses=True,
                ),
            )
        return None


class QueueService(CloudService):
    """Cloud queue service implementation."""

    def get_client(
        self,
    ) -> Optional[CloudClient]:
        """Get the appropriate queue client based on provider."""
        queue_config = self.config.get_queue_config()

        if queue_config["type"] == "sqs":
            default_region = (
                self.config.aws_config.get("region", "us-east-1") if self.config.aws_config else "us-east-1"
            )
            return cast(
                CloudClient,
                boto3.client(  # type: ignore
                    service_name="sqs",
                    region_name=queue_config.get("region", default_region),
                    profile_name=(self.config.aws_config.get("profile") if self.config.aws_config else None),
                ),
            )
        elif queue_config["type"] == "pubsub":
            return cast(CloudClient, pubsub_v1.PublisherClient())
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
