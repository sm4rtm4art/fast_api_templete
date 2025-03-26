"""Cloud service provider module.

This module contains the CloudServiceProvider class which is responsible for
instantiating the correct cloud service implementation based on configuration.
"""

from fast_api_template.cloud.aws import AWSCloudService
from fast_api_template.cloud.azure import AzureCloudService
from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.cloud.custom import CustomCloudService
from fast_api_template.cloud.gcp import GCPCloudService
from fast_api_template.cloud.hetzner import HetznerCloudService
from fast_api_template.cloud.local import LocalCloudService
from fast_api_template.config.cloud import CloudConfig, CloudProvider


class CloudServiceProvider:
    """Provider for creating appropriate cloud service implementations.

    This class is responsible for instantiating the correct cloud service
    implementation based on the configuration provided.
    """

    @staticmethod
    def create_service(config: CloudConfig) -> CloudService:
        """Create the appropriate cloud service based on configuration.

        Args:
            config: Cloud configuration containing provider settings

        Returns:
            An instance of the appropriate cloud service implementation
        """
        if config.provider == CloudProvider.AWS:
            return AWSCloudService(config)
        elif config.provider == CloudProvider.GCP:
            return GCPCloudService(config)
        elif config.provider == CloudProvider.AZURE:
            return AzureCloudService(config)
        elif config.provider == CloudProvider.HETZNER:
            return HetznerCloudService(config)
        elif config.provider == CloudProvider.CUSTOM:
            return CustomCloudService(config)
        else:
            return LocalCloudService(config)
