"""Test AWS cloud services using Moto mocking library.

This module demonstrates how to use Moto to mock AWS services for testing
without incurring actual AWS costs.
"""

from typing import Any, Dict, cast

import boto3
import pytest
from moto import mock_aws

from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig


class TestSettings:
    """Mock settings for AWS testing."""

    def __init__(self) -> None:
        self._settings: Dict[str, Any] = {
            "cloud": {
                "provider": "aws",
                "region": "us-west-2",
                "aws": {
                    "profile": None,  # No profile for Moto
                    "s3": {"bucket": "test-bucket"},
                    "sqs": {
                        "queue_url": None  # Will be set during test
                    },
                },
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get nested setting by dot-notation key."""
        parts = key.split(".")
        current = self._settings

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def as_dict(self) -> Dict[str, Any]:
        """Return settings as dictionary."""
        return self._settings

    def set(self, key: str, value: Any) -> None:
        """Set nested setting by dot-notation key."""
        parts = key.split(".")
        current = self._settings

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    def copy(self) -> "TestSettings":
        """Create a copy of the settings object."""
        new_settings = TestSettings()
        new_settings._settings = {
            key: value.copy() if isinstance(value, dict) else value for key, value in self._settings.items()
        }
        return new_settings


@pytest.fixture
def aws_config() -> CloudConfig:
    """Create AWS configuration for testing."""
    return CloudConfig(TestSettings())  # type: ignore


@pytest.fixture
def aws_config_with_sqs_queue(aws_config: CloudConfig) -> CloudConfig:
    """Return a modified AWS config with SQS queue URL set."""
    # Create a copy of the settings
    settings = TestSettings()

    # Create a test queue
    with mock_aws():
        sqs_client = boto3.client("sqs", region_name="us-west-2")
        response = sqs_client.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]

    # Set the queue URL in the settings
    settings.set("cloud.aws.sqs.queue_url", queue_url)

    return CloudConfig(settings)  # type: ignore


class TestAWSMoto:
    """Test AWS cloud service using Moto mocks."""

    @mock_aws
    def test_s3_operations(self, mocker: Any, aws_config: CloudConfig) -> None:
        """Test S3 storage operations with Moto."""
        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config)

        # Get the S3 client
        s3_client = cast(Any, service.get_storage_client())

        # Create a test bucket
        bucket_name = "test-bucket"
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Verify bucket exists
        response = s3_client.list_buckets()
        buckets = [bucket["Name"] for bucket in response["Buckets"]]
        assert bucket_name in buckets

        # Put an object in the bucket
        test_data = b"Hello, Moto!"
        s3_client.put_object(Bucket=bucket_name, Key="test-object.txt", Body=test_data)

        # Get the object and verify its content
        response = s3_client.get_object(Bucket=bucket_name, Key="test-object.txt")
        content = response["Body"].read()
        assert content == test_data

        # Delete the object
        s3_client.delete_object(Bucket=bucket_name, Key="test-object.txt")

        # Verify object was deleted
        with pytest.raises(s3_client.exceptions.NoSuchKey):
            s3_client.get_object(Bucket=bucket_name, Key="test-object.txt")

    @mock_aws
    def test_nonexistent_s3_object(self, mocker: Any, aws_config: CloudConfig) -> None:
        """Test handling of nonexistent S3 object."""
        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config)

        # Get the S3 client
        s3_client = cast(Any, service.get_storage_client())

        # Create a test bucket
        bucket_name = "test-bucket"
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        # Try to get a nonexistent object
        with pytest.raises(s3_client.exceptions.NoSuchKey):
            s3_client.get_object(Bucket=bucket_name, Key="nonexistent-object.txt")

    @mock_aws
    def test_nonexistent_s3_bucket(self, mocker: Any, aws_config: CloudConfig) -> None:
        """Test handling of nonexistent S3 bucket."""
        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config)

        # Get the S3 client
        s3_client = cast(Any, service.get_storage_client())

        # Try to access a nonexistent bucket
        with pytest.raises(s3_client.exceptions.NoSuchBucket):
            s3_client.get_object(Bucket="nonexistent-bucket", Key="test-object.txt")

    @mock_aws
    def test_sqs_operations(self, mocker: Any, aws_config: CloudConfig) -> None:
        """Test SQS operations with Moto."""
        # Create a test queue
        sqs_client = boto3.client("sqs", region_name="us-west-2")
        response = sqs_client.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]

        # Update config with queue_url
        mocker.patch.object(
            aws_config.settings,
            "get",
            side_effect=lambda key, default=None: (
                queue_url if key == "cloud.aws.sqs.queue_url" else TestSettings().get(key, default)
            ),
        )

        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config)

        # Get the SQS client
        queue_client = cast(Any, service.get_queue_client())

        # Send a message
        message = "Test message"
        queue_client.send_message(QueueUrl=queue_url, MessageBody=message)

        # Receive the message
        response = queue_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)

        # Verify message content
        assert "Messages" in response  # type: ignore
        assert len(response["Messages"]) == 1  # type: ignore
        assert response["Messages"][0]["Body"] == message  # type: ignore

        # Delete the message
        receipt_handle = response["Messages"][0]["ReceiptHandle"]  # type: ignore
        queue_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

        # Verify queue is empty
        response = queue_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)
        assert "Messages" not in response  # type: ignore

    @mock_aws
    def test_sqs_with_fixture(self, mocker: Any, aws_config_with_sqs_queue: CloudConfig) -> None:
        """Test SQS operations using the fixture with pre-configured queue."""
        # Create a test queue
        sqs_client = boto3.client("sqs", region_name="us-west-2")
        response = sqs_client.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]

        # Patch the settings to use our queue URL
        mocker.patch.object(
            aws_config_with_sqs_queue.settings,
            "get",
            side_effect=lambda key, default=None: (
                queue_url if key == "cloud.aws.sqs.queue_url" else TestSettings().get(key, default)
            ),
        )

        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config_with_sqs_queue)

        # Get the SQS client
        queue_client = cast(Any, service.get_queue_client())

        # Get the queue URL from config
        queue_url = aws_config_with_sqs_queue.settings.get("cloud.aws.sqs.queue_url")
        assert queue_url is not None

        # Send a message
        message = "Test message with fixture"
        queue_client.send_message(QueueUrl=queue_url, MessageBody=message)

        # Receive the message
        response = queue_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)

        # Verify message content
        assert "Messages" in response  # type: ignore
        assert len(response["Messages"]) == 1  # type: ignore
        assert response["Messages"][0]["Body"] == message  # type: ignore

    @pytest.mark.parametrize(
        "region,bucket_name",
        [("us-west-1", "test-bucket-west1"), ("us-east-1", "test-bucket-east1"), ("eu-west-1", "test-bucket-eu")],
    )
    @mock_aws
    def test_s3_multi_region(self, mocker: Any, aws_config: CloudConfig, region: str, bucket_name: str) -> None:
        """Test S3 operations across multiple regions."""
        # Patch the region in the config
        mocker.patch.object(aws_config, "region", region)

        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config)

        # Get the S3 client with the region from config
        s3_client = boto3.client("s3", region_name=region)
        mocker.patch.object(service, "get_storage_client", return_value=s3_client)

        # Create a test bucket
        # Note: us-east-1 doesn't use LocationConstraint
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},  # type: ignore
            )

        # Verify bucket exists
        response = s3_client.list_buckets()
        buckets = [bucket["Name"] for bucket in response["Buckets"]]
        assert bucket_name in buckets

        # Test basic operations
        test_data = f"Hello from {region}!".encode()
        s3_client.put_object(Bucket=bucket_name, Key="test-object.txt", Body=test_data)

        response = s3_client.get_object(Bucket=bucket_name, Key="test-object.txt")
        content = response["Body"].read()  # type: ignore
        assert content == test_data

    @mock_aws
    def test_empty_queue_handling(self, mocker: Any, aws_config: CloudConfig) -> None:
        """Test handling of empty SQS queue."""
        # Create a test queue
        sqs_client = boto3.client("sqs", region_name="us-west-2")
        response = sqs_client.create_queue(QueueName="empty-queue")
        queue_url = response["QueueUrl"]

        # Update config with queue_url
        mocker.patch.object(
            aws_config.settings,
            "get",
            side_effect=lambda key, default=None: (
                queue_url if key == "cloud.aws.sqs.queue_url" else TestSettings().get(key, default)
            ),
        )

        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config)

        # Get the SQS client
        queue_client = cast(Any, service.get_queue_client())

        # Try to receive message from empty queue
        response = queue_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)

        # Verify no messages are returned
        assert "Messages" not in response  # type: ignore
