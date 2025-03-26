"""Cloud provider configuration and utilities."""

from enum import Enum
from typing import Optional

from dynaconf import Dynaconf


class CloudProvider(str, Enum):
    """Supported cloud providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    HETZNER = "hetzner"
    CUSTOM = "custom"
    LOCAL = "local"


class CloudConfig:
    """Cloud configuration manager."""

    def __init__(self, settings: Dynaconf):
        self.settings = settings
        self.provider = CloudProvider(settings.get("cloud.provider", "local"))
        self.region = settings.get("cloud.region", "us-east-1")
        self.project_id = settings.get("cloud.project_id")
        self.tenant_id = settings.get("cloud.tenant_id")
        self.custom_config = settings.get("cloud.custom", {})

    @property
    def is_cloud(self) -> bool:
        """Check if running in cloud environment."""
        return self.provider not in [CloudProvider.LOCAL, CloudProvider.CUSTOM]

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

    @property
    def hetzner_config(self) -> Optional[dict]:
        """Get Hetzner specific configuration."""
        if self.provider != CloudProvider.HETZNER:
            return None
        return {
            "api_token": self.settings.get("cloud.hetzner.api_token"),
            "datacenter": self.settings.get("cloud.hetzner.datacenter", "fsn1"),
            "project_id": self.settings.get("cloud.hetzner.project_id"),
        }

    @property
    def custom_provider_config(self) -> Optional[dict]:
        """Get custom provider configuration."""
        if self.provider != CloudProvider.CUSTOM:
            return None
        return self.custom_config

    def get_storage_config(self) -> dict:
        """Get cloud storage configuration based on provider."""
        if not self.is_cloud and self.provider != CloudProvider.CUSTOM:
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
        elif self.provider == CloudProvider.HETZNER:
            return {
                "type": "hetzner",
                "storage_box": self.settings.get("cloud.hetzner.storage.box_id"),
                "datacenter": self.settings.get("cloud.hetzner.datacenter", "fsn1"),
                "subdomain": self.settings.get("cloud.hetzner.storage.subdomain"),
            }
        elif self.provider == CloudProvider.CUSTOM:
            return self.settings.get("cloud.custom.storage", {})
        return {"type": "local"}

    def get_cache_config(self) -> dict:
        """Get cloud cache configuration based on provider."""
        if not self.is_cloud and self.provider != CloudProvider.CUSTOM:
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
        elif self.provider == CloudProvider.HETZNER:
            # Hetzner doesn't provide a managed Redis service directly
            # This configuration would be for a self-hosted Redis on Hetzner Cloud
            return {
                "type": "redis",
                "host": self.settings.get("cloud.hetzner.cache.host"),
                "port": self.settings.get("cloud.hetzner.cache.port", 6379),
                "password": self.settings.get("cloud.hetzner.cache.password"),
            }
        elif self.provider == CloudProvider.CUSTOM:
            return self.settings.get("cloud.custom.cache", {})
        return {"type": "local"}

    def get_queue_config(self) -> dict:
        """Get cloud queue configuration based on provider."""
        if not self.is_cloud and self.provider != CloudProvider.CUSTOM:
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
        elif self.provider == CloudProvider.HETZNER:
            # Hetzner doesn't provide a managed message queue service directly
            # This configuration would be for a self-hosted RabbitMQ on Hetzner Cloud
            return {
                "type": "rabbitmq",
                "host": self.settings.get("cloud.hetzner.queue.host"),
                "port": self.settings.get("cloud.hetzner.queue.port", 5672),
                "username": self.settings.get("cloud.hetzner.queue.username", "guest"),
                "password": self.settings.get("cloud.hetzner.queue.password", "guest"),
                "vhost": self.settings.get("cloud.hetzner.queue.vhost", "/"),
            }
        elif self.provider == CloudProvider.CUSTOM:
            return self.settings.get("cloud.custom.queue", {})
        return {"type": "local"}
