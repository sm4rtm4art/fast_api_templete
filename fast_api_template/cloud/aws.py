"""AWS cloud service implementation."""

from typing import Literal, Optional, cast

import boto3
import redis
from mypy_boto3_s3.client import S3Client
from mypy_boto3_sqs.client import SQSClient
from redis import Redis

from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.config.cloud import CloudConfig


class AWSCloudService(CloudService):
    """AWS cloud service implementation."""

    def get_storage_client(self) -> Optional[S3Client]:
        """Get AWS S3 client.

        Returns:
            Optional[S3Client]: The S3 client if AWS config is available,
            None otherwise.
        """
        if not self.config.aws_config:
            return None
        return cast(
            S3Client,
            boto3.client(
                service_name=Literal["s3"],  # type: ignore
                region_name=self.config.aws_config["region"],
                profile_name=self.config.aws_config["profile"],
            ),
        )

    def get_cache_client(self) -> Optional[Redis]:
        """Get AWS ElastiCache client.

        Returns:
            Optional[Redis]: The Redis client if ElastiCache config is
            available, None otherwise.
        """
        cache_config = self.config.get_cache_config()
        if cache_config["type"] != "elasticache":
            return None
        return redis.Redis(
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
        if queue_config["type"] != "sqs":
            return None
        return cast(
            SQSClient,
            boto3.client(
                service_name=Literal["sqs"],  # type: ignore
                region_name=queue_config["region"],
                profile_name=self.config.aws_config["profile"],
            ),
        )
