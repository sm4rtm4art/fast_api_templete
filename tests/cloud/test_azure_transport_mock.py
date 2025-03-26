"""Test Azure cloud services using transport-based mocking.

This module demonstrates how to use the transport-based mock approach with Azure SDK,
which is the recommended approach from the Azure SDK team for mocking Azure services.
"""

import json
from collections import namedtuple
from unittest.mock import MagicMock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from azure.servicebus import ServiceBusClient
from azure.storage.blob import BlobServiceClient

from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from tests.cloud.conftest import AzureMockTransport
from tests.cloud.test_azure_mock import TestCloudConfig

# Create a simple internal response type that matches what Azure SDK expects
InternalResponse = namedtuple("InternalResponse", ["status_code", "headers", "text", "reason", "content_type", "body"])


@pytest.mark.skip(reason="Complex Azure authentication mocking needed")
class TestAzureTransportMock:
    """Test Azure cloud services using the transport-based mocking approach."""

    def test_blob_storage_operations(self, azure_config):
        """Test Azure Blob Storage operations using transport mocks."""
        # Convert to TestCloudConfig for mocking
        azure_config = TestCloudConfig(azure_config.settings)

        # Create mock responses for different operations
        test_container_name = "test-container"
        test_blob_name = "test-blob.txt"
        test_content = b"Hello, Azure transport mock!"

        # Set up mock responses
        mock_responses = {}

        # Mock creating a container
        container_create_req = HttpRequest(
            "PUT", f"https://teststorage.blob.core.windows.net/{test_container_name}?restype=container"
        )
        container_response = InternalResponse(
            status_code=201,
            headers={"ETag": "0x8DA1E5CA36F2E75"},
            text="",
            reason="Created",
            content_type="application/json",
            body=b"",
        )
        mock_responses["create_container"] = HttpResponse(
            request=container_create_req, internal_response=container_response
        )

        # Mock uploading a blob
        blob_upload_req = HttpRequest(
            "PUT", f"https://teststorage.blob.core.windows.net/{test_container_name}/{test_blob_name}"
        )
        upload_response = InternalResponse(
            status_code=201,
            headers={"ETag": "0x8DA1E5CA36F2E76", "Content-MD5": "base64-encoded-md5"},
            text="",
            reason="Created",
            content_type="application/json",
            body=b"",
        )
        mock_responses["upload_blob"] = HttpResponse(request=blob_upload_req, internal_response=upload_response)

        # Mock downloading a blob
        blob_download_req = HttpRequest(
            "GET", f"https://teststorage.blob.core.windows.net/{test_container_name}/{test_blob_name}"
        )
        download_response = InternalResponse(
            status_code=200,
            headers={
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(test_content)),
                "ETag": "0x8DA1E5CA36F2E76",
            },
            text=test_content.decode(),
            reason="OK",
            content_type="application/octet-stream",
            body=test_content,
        )
        mock_responses["download_blob"] = HttpResponse(request=blob_download_req, internal_response=download_response)

        # Create mock transport with URL pattern mapping for simplicity
        mock_transport = AzureMockTransport(
            status_codes={
                "?restype=container": 201,  # Container operations
                f"/{test_container_name}/{test_blob_name}": 200,  # Blob operations
            }
        )
        mock_transport.responses = mock_responses

        # Create client with mock transport
        connection_string = (
            "DefaultEndpointsProtocol=https;AccountName=teststorage;AccountKey=testkey;EndpointSuffix=core.windows.net"
        )

        # Set the azure_config for testing
        azure_config.azure_config = {"connection_string": connection_string}

        # Get the cloud service
        service = CloudServiceProvider.create_service(azure_config)

        # Create a blob service client with our mock transport
        blob_service_client = BlobServiceClient.from_connection_string(connection_string, transport=mock_transport)

        # Patch the get_storage_client method to return our mocked client
        with patch.object(service, "get_storage_client", return_value=blob_service_client):
            # Get the storage client
            storage_client = service.get_storage_client()

            # Test creating a container
            container_client = storage_client.create_container(test_container_name)
            assert container_client is not None

            # Test uploading a blob
            blob_client = container_client.get_blob_client(test_blob_name)
            result = blob_client.upload_blob(test_content)
            assert result is not None

            # Test downloading a blob
            download_stream = blob_client.download_blob()
            content = download_stream.readall()
            assert content == test_content

            # Verify the transport was used - requests should be in the recorded list
            assert len(mock_transport.requests) >= 3  # At least 3 requests (create, upload, download)

    def test_servicebus_operations(self, azure_config):
        """Test Azure Service Bus operations using transport mocks."""
        # Convert to TestCloudConfig for mocking
        azure_config = TestCloudConfig(azure_config.settings)

        # Create mock responses for different operations
        test_queue_name = "test-queue"
        test_message = "Test message from transport mock"

        # Set up mock responses
        mock_responses = {}

        # Mock sending a message
        send_msg_req = HttpRequest("POST", f"https://test-namespace.servicebus.windows.net/{test_queue_name}/messages")
        send_response = InternalResponse(
            status_code=201,
            headers={"Content-Type": "application/json"},
            text="",
            reason="Created",
            content_type="application/json",
            body=b"",
        )
        mock_responses["send_message"] = HttpResponse(request=send_msg_req, internal_response=send_response)

        # Mock receiving a message
        receive_msg_req = HttpRequest(
            "POST", f"https://test-namespace.servicebus.windows.net/{test_queue_name}/messages/head"
        )
        receive_response = InternalResponse(
            status_code=200,
            headers={
                "Content-Type": "application/json",
                "BrokerProperties": json.dumps(
                    {"MessageId": "test-message-id", "SequenceNumber": 1, "EnqueuedTimeUtc": "2023-01-01T00:00:00Z"}
                ),
            },
            text=test_message,
            reason="OK",
            content_type="application/json",
            body=test_message.encode(),
        )
        mock_responses["receive_message"] = HttpResponse(request=receive_msg_req, internal_response=receive_response)

        # Create mock transport with URL pattern mapping for simplicity
        mock_transport = AzureMockTransport(
            status_codes={
                "/messages": 201,  # Message operations
            }
        )
        mock_transport.responses = mock_responses

        # Create connection string
        connection_string = "Endpoint=sb://test-namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=testkey"

        # Set the azure_config for testing
        azure_config.azure_config = {"servicebus_connection_string": connection_string}

        # Get the cloud service
        service = CloudServiceProvider.create_service(azure_config)

        # Create a service bus client with our mock transport
        servicebus_client = ServiceBusClient.from_connection_string(connection_string, transport=mock_transport)

        # Patch the get_queue_client method to return our mocked client
        with patch.object(service, "get_queue_client", return_value=servicebus_client):
            # Get the queue client
            queue_client = service.get_queue_client()

            # Test sending a message
            with queue_client.get_queue_sender(queue_name=test_queue_name) as sender:
                sender.send_messages(test_message)

            # Test receiving a message (need a custom mock for peek_messages method)
            with queue_client.get_queue_receiver(queue_name=test_queue_name) as receiver:
                # We need to mock the receiver methods directly as they don't use the transport
                receiver._internal_receiver.peek_messages = MagicMock(
                    return_value=[MagicMock(body=test_message.encode())]
                )
                messages = receiver.peek_messages(max_message_count=1)

                assert len(messages) == 1
                assert messages[0].body == test_message.encode()

            # Verify the transport was used for sending
            assert any("/messages" in req[0].url for req in mock_transport.requests)

    def test_error_handling(self, azure_config):
        """Test Azure error handling using transport mocks."""
        # Convert to TestCloudConfig for mocking
        azure_config = TestCloudConfig(azure_config.settings)

        test_container_name = "nonexistent-container"
        test_blob_name = "nonexistent-blob.txt"

        # Create a 404 response for nonexistent container
        error_req = HttpRequest("GET", f"https://teststorage.blob.core.windows.net/{test_container_name}")
        error_response = InternalResponse(
            status_code=404,
            headers={"Content-Type": "application/xml", "x-ms-error-code": "ContainerNotFound"},
            text='<?xml version="1.0" encoding="utf-8"?><Error><Code>ContainerNotFound</Code></Error>',
            reason="Not Found",
            content_type="application/xml",
            body=b'<?xml version="1.0" encoding="utf-8"?><Error><Code>ContainerNotFound</Code></Error>',
        )

        # Create mock transport with error responses
        mock_transport = AzureMockTransport()
        mock_transport.send = MagicMock(return_value=HttpResponse(request=error_req, internal_response=error_response))

        # Create client with mock transport
        connection_string = (
            "DefaultEndpointsProtocol=https;AccountName=teststorage;AccountKey=testkey;EndpointSuffix=core.windows.net"
        )

        # Set the azure_config for testing
        azure_config.azure_config = {"connection_string": connection_string}

        # Get the cloud service
        service = CloudServiceProvider.create_service(azure_config)

        # Create a blob service client with our mock transport
        blob_service_client = BlobServiceClient.from_connection_string(connection_string, transport=mock_transport)

        # Patch the get_storage_client method to return our mocked client
        with patch.object(service, "get_storage_client", return_value=blob_service_client):
            # Get the storage client
            storage_client = service.get_storage_client()

            # Test accessing a non-existent container
            container_client = storage_client.get_container_client(test_container_name)

            # Accessing the non-existent container should raise an error
            with pytest.raises(ResourceNotFoundError):
                container_client.get_container_properties()
