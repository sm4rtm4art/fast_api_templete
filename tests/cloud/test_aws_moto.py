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
from stubs.boto_stubs import S3ResponseTypeDef, SQSResponseTypeDef
from tests.cloud.conftest import MockSettings


@pytest.fixture
def aws_config() -> CloudConfig:
    """Create AWS configuration for testing."""
    return CloudConfig(MockSettings())  # type: ignore


@pytest.fixture
def aws_config_with_sqs_queue_for_test(aws_config: CloudConfig) -> CloudConfig:
    """Return a modified AWS config with SQS queue URL set."""
    # Create a copy of the settings
    settings = MockSettings()

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
        response: S3ResponseTypeDef = s3_client.get_object(Bucket=bucket_name, Key="test-object.txt")
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
                queue_url if key == "cloud.aws.sqs.queue_url" else MockSettings().get(key, default)
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
        response: SQSResponseTypeDef = queue_client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1
        )

        # Verify message content
        assert "Messages" in response
        assert len(response["Messages"]) == 1
        assert response["Messages"][0]["Body"] == message

        # Delete the message
        receipt_handle = response["Messages"][0]["ReceiptHandle"]
        queue_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)

        # Verify queue is empty
        response = queue_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)
        assert "Messages" not in response

    @mock_aws
    def test_sqs_with_fixture(self, mocker: Any, aws_config_with_sqs_queue_for_test: CloudConfig) -> None:
        """Test SQS operations using the fixture with pre-configured queue."""
        # Create a test queue
        sqs_client = boto3.client("sqs", region_name="us-west-2")
        response = sqs_client.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]

        # Patch the settings to use our queue URL
        mocker.patch.object(
            aws_config_with_sqs_queue_for_test.settings,
            "get",
            side_effect=lambda key, default=None: (
                queue_url if key == "cloud.aws.sqs.queue_url" else MockSettings().get(key, default)
            ),
        )

        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config_with_sqs_queue_for_test)

        # Get the SQS client
        queue_client = cast(Any, service.get_queue_client())

        # Get the queue URL from config
        queue_url = aws_config_with_sqs_queue_for_test.settings.get("cloud.aws.sqs.queue_url")
        assert queue_url is not None

        # Send a message
        message = "Test message with fixture"
        queue_client.send_message(QueueUrl=queue_url, MessageBody=message)

        # Receive the message
        response: SQSResponseTypeDef = queue_client.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1
        )

        # Verify message content
        assert "Messages" in response
        assert len(response["Messages"]) == 1
        assert response["Messages"][0]["Body"] == message

    @pytest.mark.parametrize(
        "region,bucket_name",
        [("us-west-1", "test-bucket-west1"), ("us-east-1", "test-bucket-east1"), ("eu-west-1", "test-bucket-eu")],
    )
    @mock_aws
    def test_s3_multi_region(self, mocker: Any, aws_config: CloudConfig, region: str, bucket_name: str) -> None:
        """Test S3 operations in different regions."""
        # Create an S3 client for specific region
        s3_client = boto3.client("s3", region_name=region)

        # Create a test bucket
        if region == "us-east-1":
            # us-east-1 is the default and doesn't accept LocationConstraint
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

        # Override region in mock settings
        mocker.patch.object(
            aws_config.settings,
            "get",
            side_effect=lambda key, default=None: (
                region
                if key == "cloud.region"
                else bucket_name
                if key == "cloud.aws.s3.bucket"
                else MockSettings().get(key, default)
            ),
        )

        # Get the service with the region
        service = CloudServiceProvider.create_service(aws_config)
        client = cast(Any, service.get_storage_client())

        # Test the client's region
        # We can't directly check the client's region, but we can check that it can access the bucket
        buckets = client.list_buckets()["Buckets"]
        bucket_names = [bucket["Name"] for bucket in buckets]
        assert bucket_name in bucket_names

    @mock_aws
    def test_empty_queue_handling(self, mocker: Any, aws_config: CloudConfig) -> None:
        """Test handling of empty SQS queue."""
        # Create a test queue
        sqs_client = boto3.client("sqs", region_name="us-west-2")
        response = sqs_client.create_queue(QueueName="test-queue")
        queue_url = response["QueueUrl"]

        # Update config with queue_url
        mocker.patch.object(
            aws_config.settings,
            "get",
            side_effect=lambda key, default=None: (
                queue_url if key == "cloud.aws.sqs.queue_url" else MockSettings().get(key, default)
            ),
        )

        # Get the AWS service
        service = CloudServiceProvider.create_service(aws_config)

        # Get the SQS client
        queue_client = cast(Any, service.get_queue_client())

        # Receive message from empty queue (should return empty response without Messages)
        response = queue_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=1)

        # Verify no messages
        assert "Messages" not in response
