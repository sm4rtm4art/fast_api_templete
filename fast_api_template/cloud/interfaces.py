"""Cloud service interfaces."""

from abc import ABC, abstractmethod
from typing import Any

from fast_api_template.config.cloud import CloudConfig


class CloudService(ABC):
    """Abstract base class for cloud services."""

    def __init__(self, config: CloudConfig):
        self.config = config

    @abstractmethod
    def get_storage_client(self) -> Any:
        """Get the storage client."""
        pass

    @abstractmethod
    def get_cache_client(self) -> Any:
        """Get the cache client."""
        pass

    @abstractmethod
    def get_queue_client(self) -> Any:
        """Get the queue client."""
        pass
