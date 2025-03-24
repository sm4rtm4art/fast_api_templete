"""Azure cloud service implementation."""

from typing import Any, Optional

from azure.identity import DefaultAzureCredential
from azure.mgmt.redis import RedisManagementClient
from azure.servicebus import ServiceBusClient
from azure.storage.blob import BlobServiceClient

from fast_api_template.cloud.cloud_service_interface import CloudService


class AzureCloudService(CloudService):
    """Azure cloud service implementation."""

    def get_storage_client(self) -> Optional[Any]:
        """Get Azure Blob Storage client."""
        if not self.config.azure_config:
            return None
        return BlobServiceClient.from_connection_string(self.config.azure_config["connection_string"])

    def get_cache_client(self) -> Optional[Any]:
        """Get Azure Cache client."""
        if not self.config.azure_config:
            return None
        return RedisManagementClient(
            credential=DefaultAzureCredential(),
            subscription_id=self.config.azure_config["subscription_id"],
        )

    def get_queue_client(self) -> Optional[Any]:
        """Get Azure Service Bus client."""
        if not self.config.azure_config:
            return None
        return ServiceBusClient.from_connection_string(self.config.azure_config["connection_string"])
