"""Cloud provider configuration and utilities."""

from enum import Enum
from typing import Optional

from dynaconf import Dynaconf


class CloudProvider(str, Enum):
    """Supported cloud providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    LOCAL = "local"


class CloudConfig:
    """Cloud configuration manager."""

    def __init__(self, settings: Dynaconf):
        self.settings = settings
        self.provider = CloudProvider(settings.get("cloud.provider", "local"))
        self.region = settings.get("cloud.region", "us-east-1")
        self.project_id = settings.get("cloud.project_id")
        self.tenant_id = settings.get("cloud.tenant_id")

    @property
    def is_cloud(self) -> bool:
        """Check if running in cloud environment."""
        return self.provider != CloudProvider.LOCAL

    @property
    def aws_config(self) -> Optional[dict]:
        """Get AWS specific configuration."""
        if self.provider != CloudProvider.AWS:
            return None
        return {
            "region": self.region,
            "profile": self.settings.get("cloud.aws.profile"),
            "role_arn": self.settings.get("cloud.aws.role_arn"),
        }

    @property
    def gcp_config(self) -> Optional[dict]:
        """Get GCP specific configuration."""
        if self.provider != CloudProvider.GCP:
            return None
        return {
            "project_id": self.project_id,
            "region": self.region,
            "credentials_path": self.settings.get("cloud.gcp.credentials_path"),
        }

    @property
    def azure_config(self) -> Optional[dict]:
        """Get Azure specific configuration."""
        if self.provider != CloudProvider.AZURE:
            return None
        return {
            "tenant_id": self.tenant_id,
            "subscription_id": self.settings.get("cloud.azure.subscription_id"),
            "resource_group": self.settings.get("cloud.azure.resource_group"),
        }

    def get_storage_config(self) -> dict:
        """Get cloud storage configuration based on provider."""
        if not self.is_cloud:
            return {"type": "local"}

        if self.provider == CloudProvider.AWS:
            return {
                "type": "s3",
                "bucket": self.settings.get("cloud.aws.s3.bucket"),
                "region": self.region,
            }
        elif self.provider == CloudProvider.GCP:
            return {
                "type": "gcs",
                "bucket": self.settings.get("cloud.gcp.storage.bucket"),
                "project_id": self.project_id,
            }
        elif self.provider == CloudProvider.AZURE:
            return {
                "type": "azure",
                "container": self.settings.get("cloud.azure.storage.container"),
                "account_name": self.settings.get("cloud.azure.storage.account_name"),
            }
        return {"type": "local"}

    def get_cache_config(self) -> dict:
        """Get cloud cache configuration based on provider."""
        if not self.is_cloud:
            return {"type": "local"}

        if self.provider == CloudProvider.AWS:
            return {
                "type": "elasticache",
                "endpoint": self.settings.get("cloud.aws.elasticache.endpoint"),
                "port": self.settings.get("cloud.aws.elasticache.port", 6379),
            }
        elif self.provider == CloudProvider.GCP:
            return {
                "type": "memorystore",
                "instance": self.settings.get("cloud.gcp.memorystore.instance"),
                "region": self.region,
            }
        elif self.provider == CloudProvider.AZURE:
            return {
                "type": "cache",
                "name": self.settings.get("cloud.azure.cache.name"),
                "resource_group": self.settings.get("cloud.azure.resource_group"),
            }
        return {"type": "local"}

    def get_queue_config(self) -> dict:
        """Get cloud queue configuration based on provider."""
        if not self.is_cloud:
            return {"type": "local"}

        if self.provider == CloudProvider.AWS:
            return {
                "type": "sqs",
                "queue_url": self.settings.get("cloud.aws.sqs.queue_url"),
                "region": self.region,
            }
        elif self.provider == CloudProvider.GCP:
            return {
                "type": "pubsub",
                "topic": self.settings.get("cloud.gcp.pubsub.topic"),
                "subscription": self.settings.get("cloud.gcp.pubsub.subscription"),
                "project_id": self.project_id,
            }
        elif self.provider == CloudProvider.AZURE:
            return {
                "type": "servicebus",
                "namespace": self.settings.get("cloud.azure.servicebus.namespace"),
                "queue": self.settings.get("cloud.azure.servicebus.queue"),
            }
        return {"type": "local"}
