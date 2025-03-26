"""Hetzner Cloud service implementation."""

from typing import Any, Optional

import requests

from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.config.cloud import CloudConfig


class HetznerCloudService(CloudService):
    """Implementation of CloudService for Hetzner Cloud.

    Hetzner is a German cloud provider that offers competitive pricing
    and European data center locations with GDPR compliance.
    """

    def __init__(self, config: CloudConfig):
        """Initialize the Hetzner cloud service with configuration.

        Args:
            config: Cloud configuration containing Hetzner-specific settings
        """
        super().__init__(config)
        hetzner_config = config.hetzner_config or {}
        self.api_token = hetzner_config.get("api_token")
        self.datacenter = hetzner_config.get("datacenter", "fsn1")

    def get_storage_client(self) -> Optional[Any]:
        """Get the storage client for Hetzner Storage Box operations.

        Returns:
            A client object for Hetzner Storage Box or None if not configured
        """
        if not self.api_token:
            return None

        # In a real implementation, this would return a Hetzner Storage Box client
        # For now, we'll return a simple HTTP session with the API token
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"})
        return session

    def get_cache_client(self) -> Optional[Any]:
        """Get the cache client for Hetzner managed Redis.

        Returns:
            A client object for interacting with Hetzner managed Redis or None if not configured
        """
        # Hetzner doesn't provide a managed Redis service directly
        # In a real implementation, this might connect to a Redis instance running on Hetzner Cloud
        return None

    def get_queue_client(self) -> Optional[Any]:
        """Get the queue client for message queue operations.

        Returns:
            A client object for interacting with message queues or None if not configured
        """
        # Hetzner doesn't provide a managed message queue service directly
        # In a real implementation, this might connect to a RabbitMQ or Kafka instance
        # running on Hetzner Cloud
        return None
