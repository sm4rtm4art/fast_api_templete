"""Cloud provider package."""

from fast_api_template.cloud.aws import AWSCloudService
from fast_api_template.cloud.azure import AzureCloudService
from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.cloud.gcp import GCPCloudService
from fast_api_template.cloud.local import LocalCloudService

__all__ = [
    "CloudService",
    "CloudServiceProvider",
    "AWSCloudService",
    "AzureCloudService",
    "GCPCloudService",
    "LocalCloudService",
]
