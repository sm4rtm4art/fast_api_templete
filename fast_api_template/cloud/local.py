"""Local cloud service implementation."""

from typing import Any

from fast_api_template.cloud.cloud_service_interface import CloudService


class LocalCloudService(CloudService):
    """Local cloud service implementation."""

    def get_storage_client(self) -> Any:
        """Get local storage client."""
        return None  # Implement local storage if needed

    def get_cache_client(self) -> Any:
        """Get local cache client."""
        return None  # Implement local cache if needed

    def get_queue_client(self) -> Any:
        """Get local queue client."""
        return None  # Implement local queue if needed
