"""Test AWS cloud service implementation."""

from unittest.mock import MagicMock, patch

import pytest

from fast_api_template.cloud.aws import AWSCloudService
from fast_api_template.config.cloud import CloudConfig


class TestAWSCloudService:
    """Test suite for AWS cloud service."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config for AWS."""
        config = MagicMock(spec=CloudConfig)
        config.provider = "aws"
        config.region = "us-west-2"

        # Mock the aws_config property
        aws_config = {
            "region": "us-west-2",
            "profile": "test-profile",
            "role_arn": "arn:aws:iam::123456789012:role/test-role",
        }
        config.aws_config = aws_config

        # Mock the get_storage_config method
        storage_config = {"type": "s3", "bucket": "test-bucket", "region": "us-west-2"}
        config.get_storage_config.return_value = storage_config

        return config

    @patch("boto3.client")
    @patch("boto3.resource")
    def test_get_storage_client(self, mock_resource, mock_client, mock_config):
        """Test getting S3 storage client."""
        # Setup
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        mock_resource.return_value = mock_s3  # Use mock_resource to avoid vulture warning

        # Execute
        service = AWSCloudService(mock_config)
        client = service.get_storage_client()

        # Verify
        assert client is mock_s3
        mock_client.assert_called_once_with(service_name="s3", region_name="us-west-2", profile_name="test-profile")

    @patch("redis.Redis")
    def test_get_cache_client(self, mock_redis, mock_config):
        """Test getting ElastiCache client."""
        # Setup
        mock_config.get_cache_config.return_value = {"type": "elasticache", "endpoint": "test-endpoint", "port": 6379}

        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        # Execute
        service = AWSCloudService(mock_config)
        client = service.get_cache_client()

        # Verify
        assert client is mock_redis_instance
        mock_redis.assert_called_once_with(host="test-endpoint", port=6379, decode_responses=True)

    @patch("boto3.client")
    def test_get_queue_client(self, mock_client, mock_config):
        """Test getting SQS queue client."""
        # Setup
        mock_config.get_queue_config.return_value = {
            "type": "sqs",
            "queue_url": ("https://sqs.us-west-2.amazonaws.com/123456789012/test-queue"),
            "region": "us-west-2",
        }

        mock_sqs = MagicMock()
        mock_client.return_value = mock_sqs

        # Execute
        service = AWSCloudService(mock_config)
        client = service.get_queue_client()

        # Verify
        assert client is mock_sqs
        mock_client.assert_called_once_with(service_name="sqs", region_name="us-west-2", profile_name="test-profile")
