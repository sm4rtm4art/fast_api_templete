"""Integration tests for cloud providers.

These tests validate the cloud provider integration with minimal mocking.
They validate the interfaces work correctly even when implementation details
change.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig, CloudProvider


@pytest.fixture
def aws_settings():
    """Create a real-ish AWS settings object."""

    class Settings:
        def get(self, key, default=None):
            if key == "cloud.provider":
                return "aws"
            if key == "cloud.region":
                return os.environ.get("AWS_DEFAULT_REGION", "us-west-2")
            if key == "cloud.aws.profile":
                return "default"
            return default

    return Settings()


@pytest.fixture
def hetzner_settings():
    """Create a real-ish Hetzner settings object."""

    class Settings:
        def get(self, key, default=None):
            if key == "cloud.provider":
                return "hetzner"
            if key == "cloud.region":
                return "eu-central"
            if key == "cloud.hetzner.api_token":
                return os.environ.get("HETZNER_API_TOKEN")
            if key == "cloud.hetzner.datacenter":
                return "fsn1"
            return default

    return Settings()


@pytest.fixture
def custom_settings():
    """Create a real-ish custom settings object with MinIO."""

    class Settings:
        def get(self, key, default=None):
            if key == "cloud.provider":
                return "custom"
            if key == "cloud.custom.storage.type":
                return "minio"
            if key == "cloud.custom.storage.endpoint":
                return "localhost:9000"
            if key == "cloud.custom.storage.access_key":
                return os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
            if key == "cloud.custom.storage.secret_key":
                return os.environ.get("MINIO_SECRET_KEY", "minioadmin")
            if key == "cloud.custom.storage":
                return {
                    "type": "minio",
                    "endpoint": "localhost:9000",
                    "access_key": os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
                    "secret_key": os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
                    "secure": False,
                }
            if key == "cloud.custom":
                return {"storage": self.get("cloud.custom.storage"), "name": "test-custom"}
            return default

    return Settings()


@pytest.mark.integration
class TestCloudProviderIntegration:
    """Test cloud provider integration."""

    @patch("boto3.client")
    @patch("boto3.resource")
    def test_aws_factory_integration(self, mock_resource, mock_client, aws_settings, cloud_test_env):
        """Test AWS cloud provider factory integration."""
        # Setup
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3

        # Execute - create the cloud service
        config = CloudConfig(aws_settings)
        service = CloudServiceProvider.create_service(config)

        # Get the storage client
        client = service.get_storage_client()

        # Verify that boto3 client was created with correct parameters
        assert client is mock_s3
        mock_client.assert_called_once_with(service_name="s3", region_name="us-west-2", profile_name="default")

    @patch("requests.Session")
    def test_hetzner_factory_integration(self, mock_session, hetzner_settings, cloud_test_env):
        """Test Hetzner cloud provider factory integration."""
        # Setup
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Execute - create the cloud service
        config = CloudConfig(hetzner_settings)
        service = CloudServiceProvider.create_service(config)

        # Get the storage client
        client = service.get_storage_client()

        # Verify that Session was created with correct headers
        assert client is mock_session_instance
        mock_session_instance.headers.update.assert_called_once_with(
            {"Authorization": f'Bearer {cloud_test_env["HETZNER_API_TOKEN"]}', "Content-Type": "application/json"}
        )

    @patch("minio.Minio")
    def test_custom_factory_integration(self, mock_minio, custom_settings, cloud_test_env):
        """Test Custom cloud provider factory integration with MinIO."""
        # Setup
        mock_minio_instance = MagicMock()
        mock_minio.return_value = mock_minio_instance

        # Execute - create the cloud service
        config = CloudConfig(custom_settings)
        service = CloudServiceProvider.create_service(config)

        # Get the storage client
        client = service.get_storage_client()

        # Verify that Minio client was created with correct parameters
        assert client is mock_minio_instance
        mock_minio.assert_called_once_with(
            endpoint="localhost:9000",
            access_key=cloud_test_env["MINIO_ACCESS_KEY"],
            secret_key=cloud_test_env["MINIO_SECRET_KEY"],
            secure=False,
        )
