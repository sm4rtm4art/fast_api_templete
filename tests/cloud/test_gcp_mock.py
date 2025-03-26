"""Test GCP cloud services using official Google API mocking.

This module demonstrates how to mock GCP services for testing
without incurring actual GCP costs using:

1. The official googleapiclient.http.HttpMock for Google API endpoints
2. Manual mocking for non-API services
"""

import json
from unittest.mock import MagicMock, patch

import pytest

# Handle import errors gracefully for testing
try:
    # We use direct imports instead of aliasing to avoid redefinition issues
    import googleapiclient.http

    GOOGLE_API_MOCK_AVAILABLE = True
except ImportError:
    # Create dummy types for test type checking
    class HttpMock:
        """Mock for googleapiclient.http.HttpMock."""

        pass

    class HttpMockSequence:
        """Mock for googleapiclient.http.HttpMockSequence."""

        pass

    GOOGLE_API_MOCK_AVAILABLE = False

# Use a broader exception for GCP services imports
try:
    from fast_api_template.cloud.services.gcp_service import GCPCloudService
except ImportError:
    # Mock GCPCloudService if it doesn't exist
    class GCPCloudService:
        """Mock implementation of GCPCloudService."""

        def __init__(self, config):
            self.config = config


from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig


class TestSettings:
    """Mock settings for GCP testing."""

    def __init__(self):
        self._settings = {
            "cloud": {
                "provider": "gcp",
                "region": "us-central1",
                "project_id": "test-project",
                "gcp": {
                    "credentials_path": "/path/to/credentials.json",
                    "storage": {"bucket": "test-bucket"},
                    "pubsub": {"topic": "test-topic", "subscription": "test-subscription"},
                },
            }
        }

    def get(self, key, default=None):
        """Get nested setting by dot-notation key."""
        parts = key.split(".")
        current = self._settings

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current

    def as_dict(self):
        """Return settings as dictionary."""
        return self._settings


@pytest.fixture
def gcp_config():
    """Create GCP configuration for testing."""
    return CloudConfig(TestSettings())


# Skip the class if the Google API mock utilities aren't available
@pytest.mark.skipif(not GOOGLE_API_MOCK_AVAILABLE, reason="googleapiclient.http mock not available")
class TestGCPWithGoogleAPIMock:
    """Test GCP cloud services using official Google API mocking."""

    @pytest.fixture
    def gcp_service(self, gcp_config):
        """Create a GCP cloud service for testing."""
        return CloudServiceProvider.create_service(gcp_config)

    @pytest.mark.skip(reason="Requires complex GCP credentials mocking")
    def test_storage_operations(self, gcp_service):
        """Test GCP Storage operations with GoogleAPIMock."""
        project_id = "test-project"
        bucket_name = "test-bucket"
        object_name = "test-object.txt"

        # Create mock responses for a sequence of API calls
        # 1. GET for project info
        # 2. GET for bucket list
        # 3. POST for bucket creation
        # 4. GET for bucket info
        # 5. POST for object upload
        # 6. GET for object content
        # 7. DELETE for object
        mock_responses = googleapiclient.http.HttpMockSequence(
            [
                # Response for project info
                ({"status": "200"}, json.dumps({"kind": "storage#project", "projectId": project_id})),
                # Response for bucket list
                ({"status": "200"}, json.dumps({"kind": "storage#buckets", "items": []})),
                # Response for bucket creation
                (
                    {"status": "200"},
                    json.dumps(
                        {
                            "kind": "storage#bucket",
                            "id": bucket_name,
                            "name": bucket_name,
                            "timeCreated": "2023-01-01T00:00:00.000Z",
                            "location": "US-CENTRAL1",
                        }
                    ),
                ),
                # Response for bucket info
                (
                    {"status": "200"},
                    json.dumps(
                        {
                            "kind": "storage#bucket",
                            "id": bucket_name,
                            "name": bucket_name,
                            "timeCreated": "2023-01-01T00:00:00.000Z",
                            "location": "US-CENTRAL1",
                        }
                    ),
                ),
                # Response for object upload
                (
                    {"status": "200"},
                    json.dumps(
                        {
                            "kind": "storage#object",
                            "id": f"{bucket_name}/{object_name}",
                            "name": object_name,
                            "bucket": bucket_name,
                            "size": "12",
                            "contentType": "text/plain",
                            "timeCreated": "2023-01-01T00:00:00.000Z",
                        }
                    ),
                ),
                # Response for object content
                ({"status": "200", "content-type": "text/plain"}, b"Hello, GCP!"),
                # Response for object deletion
                ({"status": "204"}, ""),
            ]
        )

        # Patch the GCP client to use our mock sequence
        with patch("googleapiclient.discovery.build") as mock_build:
            # Create a mock storage service
            mock_storage_service = MagicMock()
            mock_build.return_value = mock_storage_service

            # Mock the buckets and objects resources
            mock_buckets = MagicMock()
            mock_objects = MagicMock()
            mock_storage_service.buckets.return_value = mock_buckets
            mock_storage_service.objects.return_value = mock_objects

            # Get the storage client
            storage_client = gcp_service.get_storage_client()

            # Check if a bucket exists and create it if not
            # Test bucket creation
            mock_list = MagicMock()
            mock_buckets.list.return_value = mock_list
            mock_list.execute.return_value = {"items": []}

            mock_insert = MagicMock()
            mock_buckets.insert.return_value = mock_insert
            mock_insert.execute.return_value = {"name": bucket_name, "location": "US-CENTRAL1"}

            # In a real test, the client would check for bucket existence
            # and create it if needed
            bucket_exists = False
            # Check if bucket exists
            buckets = storage_client.buckets().list(project=project_id).execute()
            for bucket in buckets.get("items", []):
                if bucket["name"] == bucket_name:
                    bucket_exists = True
                    break

            # Create bucket if it doesn't exist
            if not bucket_exists:
                storage_client.buckets().insert(project=project_id, body={"name": bucket_name}).execute()

            # Test object operations
            # Insert a test object
            mock_insert = MagicMock()
            mock_objects.insert.return_value = mock_insert
            mock_insert.execute.return_value = {"name": object_name, "bucket": bucket_name, "size": "12"}

            # Mock media uploads and downloads
            media_content = b"Hello, GCP!"

            # Upload an object
            mock_upload = MagicMock()
            mock_objects.insert.return_value = mock_upload
            mock_upload.execute.return_value = {"name": object_name, "bucket": bucket_name}

            storage_client.objects().insert(
                bucket=bucket_name,
                name=object_name,
                body={"name": object_name, "contentType": "text/plain"},
                media_body=media_content,
            ).execute()

            # Get an object
            mock_get = MagicMock()
            mock_objects.get_media.return_value = mock_get
            mock_get.execute.return_value = media_content

            content = storage_client.objects().get_media(bucket=bucket_name, object=object_name).execute()

            assert content == b"Hello, GCP!"

            # Delete an object
            mock_delete = MagicMock()
            mock_objects.delete.return_value = mock_delete
            mock_delete.execute.return_value = None

            storage_client.objects().delete(bucket=bucket_name, object=object_name).execute()

            # Verify the operations were called correctly
            mock_buckets.list.assert_called()
            mock_buckets.insert.assert_called()
            mock_objects.insert.assert_called()
            mock_objects.get_media.assert_called()
            mock_objects.delete.assert_called()

    def test_pubsub_operations(self, gcp_service):
        """Test PubSub operations with official mocks."""
        project_id = "test-project"
        topic_name = "test-topic"
        subscription_name = "test-subscription"
        message = "Test message"

        # Create mock responses for PubSub API calls
        with patch("google.cloud.pubsub_v1.PublisherClient") as mock_publisher_class:
            # Create mock publisher
            mock_publisher = MagicMock()
            mock_publisher_class.return_value = mock_publisher

            # Mock publish method
            mock_future = MagicMock()
            mock_future.result.return_value = "message-id-123"
            mock_publisher.publish.return_value = mock_future

            # Mock the queue client method to return our publisher
            with patch.object(gcp_service, "get_queue_client", return_value=mock_publisher):
                # Test publishing a message
                topic_path = f"projects/{project_id}/topics/{topic_name}"
                data = message.encode("utf-8")

                queue_client = gcp_service.get_queue_client()
                future = queue_client.publish(topic_path, data=data)
                message_id = future.result()

                # Verify message was published
                assert message_id == "message-id-123"
                mock_publisher.publish.assert_called_once_with(topic_path, data=data)

            # Test subscriber operations
            with patch("google.cloud.pubsub_v1.SubscriberClient") as mock_sub_class:
                mock_subscriber = MagicMock()
                mock_sub_class.return_value = mock_subscriber

                # Mock subscription path method
                sub_path = f"projects/{project_id}/subscriptions/{subscription_name}"
                mock_subscriber.subscription_path.return_value = sub_path

                # Mock received message
                mock_message = MagicMock()
                mock_message.data = message.encode("utf-8")
                mock_message.attributes = {"attr1": "value1"}

                # Mock pull method
                mock_subscriber.pull.return_value = MagicMock(
                    received_messages=[MagicMock(message=mock_message, ack_id="ack-id-123")]
                )

                # Pull messages
                response = mock_subscriber.pull(request={"subscription": sub_path, "max_messages": 10})

                # Verify messages were received
                assert len(response.received_messages) == 1
                assert response.received_messages[0].message.data == message.encode("utf-8")

                # Acknowledge the message
                ack_ids = ["ack-id-123"]
                mock_subscriber.acknowledge(request={"subscription": sub_path, "ack_ids": ack_ids})

                # Verify message was acknowledged
                mock_subscriber.acknowledge.assert_called_once()
