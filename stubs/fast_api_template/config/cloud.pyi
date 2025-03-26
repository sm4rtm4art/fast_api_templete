"""Type stub for CloudConfig from fast_api_template.config.cloud."""

from typing import Any, Dict, Optional, Union

from stubs.test_helpers import SettingsProtocol

class CloudConfig:
    """Cloud configuration stub.

    This class is responsible for parsing cloud configuration settings
    from various sources and providing a unified interface for cloud services.
    """

    def __init__(self, settings: SettingsProtocol) -> None:
        """Initialize with any settings object implementing the protocol."""
        ...

    def get_provider(self) -> str:
        """Get the cloud provider name."""
        ...

    def get_region(self) -> str:
        """Get the cloud region."""
        ...

    @property
    def aws_config(self) -> Dict[str, Any]:
        """Get AWS-specific configuration."""
        ...

    @property
    def azure_config(self) -> Dict[str, Any]:
        """Get Azure-specific configuration."""
        ...

    @property
    def gcp_config(self) -> Dict[str, Any]:
        """Get GCP-specific configuration."""
        ...

    @property
    def custom_config(self) -> Dict[str, Any]:
        """Get custom provider configuration."""
        ...

    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage service configuration for the current provider."""
        ...

    def get_cache_config(self) -> Dict[str, Any]:
        """Get cache service configuration for the current provider."""
        ...

    def get_queue_config(self) -> Dict[str, Any]:
        """Get queue service configuration for the current provider."""
        ...
