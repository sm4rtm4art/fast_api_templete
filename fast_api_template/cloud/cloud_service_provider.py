"""Cloud service provider factory for creating cloud service instances."""

from typing import Dict, Optional

from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.cloud.local import LocalCloudService
from fast_api_template.config.cloud import CloudConfig

# Import cloud services with try/except for each provider to handle missing
# dependencies
try:
    from fast_api_template.cloud.aws import AWSCloudService
except ImportError:
    # Define a stub class for type checking
    class AWSCloudService(CloudService):  # type: ignore
        """Placeholder for AWS cloud service when dependencies are not available."""


try:
    from fast_api_template.cloud.azure import AzureCloudService
except ImportError:
    # Define a stub class for type checking
    class AzureCloudService(CloudService):  # type: ignore
        """Placeholder for Azure cloud service when dependencies are not available."""


try:
    from fast_api_template.cloud.gcp import GCPCloudService
except ImportError:
    # Define a stub class for type checking
    class GCPCloudService(CloudService):  # type: ignore
        """Placeholder for GCP cloud service when dependencies are not available."""


try:
    from fast_api_template.cloud.hetzner import HetznerCloudService
except ImportError:
    # Define a stub class for type checking
    class HetznerCloudService(CloudService):  # type: ignore
        """Placeholder for Hetzner cloud service when dependencies are not available."""


try:
    from fast_api_template.cloud.custom import CustomCloudService
except ImportError:
    # Define a stub class for type checking
    class CustomCloudService(CloudService):  # type: ignore
        """Placeholder for Custom cloud service when dependencies are not available."""


class CloudServiceProvider:
    """Factory for creating cloud service instances."""

    @staticmethod
    def get_cloud_service(config: CloudConfig) -> Optional[CloudService]:
        """Get a cloud service instance based on configuration.

        Args:
            config: Cloud configuration object

        Returns:
            CloudService: An instance of the appropriate cloud service,
            or None if no valid provider is configured
        """
        # Default to local provider when none is specified
        provider = config.provider if config and config.provider else "local"

        # Map of provider names to service classes
        provider_map: Dict[str, type[CloudService]] = {
            "aws": AWSCloudService,
            "azure": AzureCloudService,
            "gcp": GCPCloudService,
            "hetzner": HetznerCloudService,
            "custom": CustomCloudService,
            "local": LocalCloudService,
        }

        # Return the appropriate service instance
        service_class = provider_map.get(provider.lower())
        if not service_class:
            return None

        return service_class(config)

    @staticmethod
    def create_service(config: CloudConfig) -> CloudService:
        """Create a cloud service instance (backward compatibility method).

        This method is kept for backward compatibility with existing code.
        New code should use get_cloud_service() instead.

        Args:
            config: Cloud configuration object

        Returns:
            CloudService: An instance of the appropriate cloud service
        """
        service = CloudServiceProvider.get_cloud_service(config)
        if service is None:
            # Fall back to local service if provider was invalid
            return LocalCloudService(config)
        return service
