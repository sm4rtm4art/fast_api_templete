"""GCP cloud service implementation."""

from typing import Any, Optional

import redis
from google.cloud import pubsub_v1, storage

from fast_api_template.cloud.cloud_service_interface import CloudService


class GCPCloudService(CloudService):
    """GCP cloud service implementation."""

    def get_storage_client(self) -> Optional[Any]:
        """Get GCP Storage client."""
        storage_config = self.config.get_storage_config()
        if storage_config["type"] != "gcs":
            return None
        return storage.Client(
            project=storage_config["project_id"],
            credentials=self.config.gcp_config["credentials_path"] if self.config.gcp_config else None,
        )

    def get_cache_client(self) -> Optional[Any]:
        """Get GCP Memorystore client."""
        cache_config = self.config.get_cache_config()
        if cache_config["type"] != "memorystore":
            return None
        return redis.Redis(
            host=cache_config["instance"],
            port=6379,
            decode_responses=True,
        )

    def get_queue_client(self) -> Optional[Any]:
        """Get GCP Pub/Sub client."""
        queue_config = self.config.get_queue_config()
        if queue_config["type"] != "pubsub":
            return None
        return pubsub_v1.PublisherClient()
