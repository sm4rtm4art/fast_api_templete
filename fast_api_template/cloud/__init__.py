"""Cloud service module for interacting with various cloud providers."""

# Always import the interface
from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.cloud.local import LocalCloudService

# Try to import implementations, but don't fail if dependencies are missing
# AWS is the primary supported cloud provider
try:
    from fast_api_template.cloud.aws import AWSCloudService
except ImportError:
    # Define a stub class for type checking
    class AWSCloudService(CloudService):  # type: ignore
        """Placeholder for AWS cloud service when dependencies are not available."""


# Optional providers
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


__all__ = [
    "CloudService",
    "CloudServiceProvider",
    "AWSCloudService",
    "AzureCloudService",
    "CustomCloudService",
    "GCPCloudService",
    "HetznerCloudService",
    "LocalCloudService",
]
