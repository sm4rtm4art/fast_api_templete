"""AWS cloud service implementation."""

from typing import Dict, Optional, cast

import boto3
from mypy_boto3_s3.client import S3Client
from mypy_boto3_sqs.client import SQSClient

try:
    import redis
except ImportError:
    # Optional dependency, will be handled gracefully in methods
    redis = None

from fast_api_template.cloud.cloud_service_interface import CloudService


class AWSCloudService(CloudService):
    """AWS cloud service implementation."""

    def get_client_params(self, service_name: str) -> Dict[str, str]:
        """Get common client parameters for AWS services.

        Args:
            service_name: The AWS service name (e.g., 's3', 'sqs')

        Returns:
            Dict with client parameters
        """
        # Get region based on service config or fall back to general region
        region = self.config.aws_config.get("region", "us-east-1") if self.config.aws_config else "us-east-1"
        if service_name == "sqs":
            queue_config = self.config.get_queue_config()
            if queue_config:
                region = queue_config.get("region", region)

        # Create the client parameters
        client_params = {
            "service_name": service_name,
            "region_name": region,
        }

        # Add profile only if it exists and is not None
        if self.config.aws_config:
            profile = self.config.aws_config.get("profile")
            if profile is not None:
                client_params["profile_name"] = profile

        return client_params

    def get_storage_client(self) -> Optional[S3Client]:
        """Get AWS S3 client.

        Returns:
            Optional[S3Client]: The S3 client if AWS config is available,
            None otherwise.
        """
        if not self.config.aws_config:
            return None

        client_params = self.get_client_params("s3")
        return cast(S3Client, boto3.client(**client_params))  # type: ignore

    def get_cache_client(self) -> Optional[object]:
        """Get AWS ElastiCache client.

        Returns:
            Optional[Redis]: The Redis client if ElastiCache config is
            available, None otherwise.
        """
        if redis is None:
            return None
            
        cache_config = self.config.get_cache_config()
        if not cache_config or cache_config.get("type") != "elasticache":
            return None
        return redis.Redis(  # type: ignore
            host=cache_config["endpoint"],
            port=cache_config["port"],
            decode_responses=True,
        )

    def get_queue_client(self) -> Optional[SQSClient]:
        """Get AWS SQS client.

        Returns:
            Optional[SQSClient]: The SQS client if AWS config is available,
            None otherwise.
        """
        if not self.config.aws_config:
            return None
        queue_config = self.config.get_queue_config()
        if not queue_config or queue_config.get("type") != "sqs":
            return None

        client_params = self.get_client_params("sqs")
        return cast(SQSClient, boto3.client(**client_params))  # type: ignore
