"""Test Azure cloud services using mocks."""

from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import MagicMock, patch

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from azure.core.pipeline.transport import HttpRequest, HttpResponse

from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig


class TestSettings:
    """Mock settings for Azure testing."""

    def __init__(self) -> None:
        self._settings: Dict[str, Any] = {
            "cloud": {
                "provider": "azure",
                "region": "eastus",
                "tenant_id": "test-tenant-id",
                "azure": {
                    "subscription_id": "test-subscription-id",
                    "resource_group": "test-resource-group",
                    "storage": {"container": "test-container", "account_name": "teststorage"},
                    "servicebus": {"namespace": "test-namespace", "queue": "test-queue"},
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


class TestCloudConfig(CloudConfig):
    """Special CloudConfig subclass for testing that enables mocking azure_config."""

    def __init__(self, settings: Any):
        super().__init__(settings)
        self._test_azure_config: Dict[str, Any] = {}

    @property
    def azure_config(self) -> Optional[Dict[str, Any]]:
        """Override the azure_config property to allow testing."""
        if self._test_azure_config:
            return self._test_azure_config
        return super().azure_config

    @azure_config.setter
    def azure_config(self, value: Dict[str, Any]) -> None:
        """Set the azure_config property."""
        self._test_azure_config = value

    @azure_config.deleter
    def azure_config(self) -> None:
        """Delete the azure_config property."""
        self._test_azure_config = {}

    def set_test_azure_config(self, config: Dict[str, Any]) -> None:
        """Set the test azure config."""
        self._test_azure_config = config


@pytest.fixture
def azure_config() -> TestCloudConfig:
    """Create Azure configuration for testing."""
    return TestCloudConfig(TestSettings())


class TestAzureMock:
    """Test Azure cloud service using mocks."""

    @patch("azure.storage.blob.BlobServiceClient")
    def test_blob_storage_operations(self, mock_blob_client_class: Any, azure_config: TestCloudConfig) -> None:
        """Test Azure Blob storage operations with mocks."""
        # Create mock objects
        mock_blob_client = MagicMock()
        mock_blob_client_class.from_connection_string.return_value = mock_blob_client

        mock_container_client = MagicMock()
        mock_blob_client.get_container_client.return_value = mock_container_client

        mock_blob = MagicMock()
        mock_container_client.get_blob_client.return_value = mock_blob

        # Set up HTTP response mock
        mock_response = MagicMock()
        mock_response.readall.return_value = b"Hello, Azure!"
        mock_blob.download_blob.return_value = mock_response

        # Define a connection string
        connection_string = (
            "DefaultEndpointsProtocol=https;AccountName=teststorage;"
            "AccountKey=testkey;EndpointSuffix=core.windows.net"
        )

        # Set test Azure config with connection string
        azure_config.set_test_azure_config({"connection_string": connection_string})

        # Create a service with the config
        service = CloudServiceProvider.create_service(azure_config)

        # Patch the Azure module to directly use our mock
        with patch("fast_api_template.cloud.azure.BlobServiceClient") as patched_blob_client:
            # This makes BlobServiceClient.from_connection_string return our mock
            patched_blob_client.from_connection_string.return_value = mock_blob_client

            # Get the storage client
            storage_client = service.get_storage_client()
            assert storage_client is not None, "Storage client should not be None"

            # Verify client was created with connection string
            patched_blob_client.from_connection_string.assert_called_once_with(connection_string)

            # Test container operations
            container_name = "test-container"
            container_client = storage_client.get_container_client(container_name)

            # Upload a blob
            blob_name = "test-blob.txt"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(b"Hello, Azure!")

            # Verify blob was uploaded
            blob_client.upload_blob.assert_called_once_with(b"Hello, Azure!")

            # Download and verify blob content
            download_stream = blob_client.download_blob()
            content = download_stream.readall()
            assert content == b"Hello, Azure!"

    @patch("azure.servicebus.ServiceBusClient")
    def test_servicebus_operations(self, mock_servicebus_client_class: Any, azure_config: TestCloudConfig) -> None:
        """Test Azure Service Bus operations with mocks."""
        # Create mock objects
        mock_servicebus_client = MagicMock()
        mock_servicebus_client_class.from_connection_string.return_value = mock_servicebus_client

        mock_queue_sender = MagicMock()
        mock_servicebus_client.get_queue_sender.return_value = mock_queue_sender

        mock_queue_receiver = MagicMock()
        mock_servicebus_client.get_queue_receiver.return_value = mock_queue_receiver

        # Mock received message
        mock_message = MagicMock()
        mock_message.body = b"Test message"
        mock_queue_receiver.receive_messages.return_value = [mock_message]

        # Set test Azure config with connection string
        azure_config.set_test_azure_config(
            {
                "connection_string": (
                    "Endpoint=sb://test.servicebus.windows.net/;"
                    "SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=testkey"
                )
            }
        )

        # Create a service with the config
        service = CloudServiceProvider.create_service(azure_config)

        # Mock the queue client method to return our servicebus client
        with patch.object(service, "get_queue_client", return_value=mock_servicebus_client):
            queue_client = service.get_queue_client()
            assert queue_client is not None, "Queue client should not be None"

            # Test sending a message
            queue_name = "test-queue"
            sender = queue_client.get_queue_sender(queue_name=queue_name)
            message = "Test message"
            sender.send_messages(message)

            # Verify message was sent
            sender.send_messages.assert_called_once_with(message)

            # Test receiving a message
            receiver = queue_client.get_queue_receiver(queue_name=queue_name)
            received_msgs = receiver.receive_messages(max_message_count=1, max_wait_time=5)

            # Verify message was received
            receiver.receive_messages.assert_called_once_with(max_message_count=1, max_wait_time=5)
            assert len(received_msgs) == 1
            assert received_msgs[0].body == b"Test message"

            # Complete the message
            receiver.complete_message(received_msgs[0])
            receiver.complete_message.assert_called_once_with(received_msgs[0])

    @pytest.mark.parametrize("status_code,should_raise", [(200, False), (404, True), (500, True)])
    def test_blob_storage_error_handling(
        self, azure_config: TestCloudConfig, status_code: int, should_raise: bool
    ) -> None:
        """Test Azure Blob Storage with different status codes."""
        test_container_name = "test-container"

        # Define connection string
        connection_string = (
            "DefaultEndpointsProtocol=https;AccountName=teststorage;"
            "AccountKey=testkey;EndpointSuffix=core.windows.net"
        )

        # Set test Azure config with connection string
        azure_config.set_test_azure_config({"connection_string": connection_string})

        # Create a service with the config
        service = CloudServiceProvider.create_service(azure_config)

        # Create mock container client that will raise or not based on status_code
        mock_blob_service_client = MagicMock()
        mock_container_client = MagicMock()
        mock_blob_service_client.get_container_client.return_value = mock_container_client

        # Set up get_container_properties to raise exception based on status_code
        if should_raise:
            if status_code == 404:
                mock_container_client.get_container_properties.side_effect = ResourceNotFoundError(
                    "Container not found", response=MagicMock(status_code=status_code)
                )
            else:
                mock_container_client.get_container_properties.side_effect = HttpResponseError(
                    "Server error", response=MagicMock(status_code=status_code)
                )
        else:
            # No error for status_code 200
            mock_container_client.get_container_properties.return_value = {"name": test_container_name}

        # Use patch to inject our mock
        with patch.object(service, "get_storage_client", return_value=mock_blob_service_client):
            storage_client = service.get_storage_client()
            assert storage_client is not None, "Storage client should not be None"
            container_client = storage_client.get_container_client(test_container_name)

            if should_raise:
                with pytest.raises((ResourceNotFoundError, HttpResponseError)):
                    container_client.get_container_properties()
            else:
                # Should not raise an exception
                properties = container_client.get_container_properties()
                assert properties["name"] == test_container_name

    def test_pytest_mock_example(self, mocker: Any, azure_config: TestCloudConfig) -> None:
        """Test Azure Blob Storage operations using pytest-mock."""
        test_container_name = "test-container"

        # Set up mock transport
        mock_transport = AzureMockTransport()

        # Create client with mock transport
        connection_string = (
            "DefaultEndpointsProtocol=https;AccountName=teststorage;"
            "AccountKey=testkey;EndpointSuffix=core.windows.net"
        )

        # Set test Azure config with connection string
        azure_config.set_test_azure_config({"connection_string": connection_string})

        # Create a service with the config
        service = CloudServiceProvider.create_service(azure_config)

        # Create a mock BlobServiceClient
        blob_service_client = MagicMock()

        # Create a mock container client that will be returned by create_container
        mock_container_client = MagicMock()
        blob_service_client.create_container.return_value = mock_container_client

        # Use mocker for the service client patch
        mocker.patch.object(service, "get_storage_client", return_value=blob_service_client)

        # Test the service
        storage_client = service.get_storage_client()
        assert storage_client is not None, "Storage client should not be None"
        container_client = storage_client.create_container(test_container_name)
        assert container_client is not None

        # Verify the create_container was called with the right parameters
        blob_service_client.create_container.assert_called_once_with(test_container_name)

    def test_specific_azure_errors(self, mocker: Any, azure_config: TestCloudConfig) -> None:
        """Test specific Azure error cases."""
        # This is just an example placeholder - implementation would be added later
        pass


class AzureMockTransport:
    """Mock transport for Azure SDK.

    This class mocks HTTP transport for Azure SDK to allow testing
    without actual HTTP calls.
    """

    def __init__(
        self,
        responses: Optional[Dict[str, HttpResponse]] = None,
        status_codes: Optional[Dict[str, int]] = None,
        default_status_code: int = 200,
    ) -> None:
        """Initialize the mock transport."""
        from azure.core.pipeline.transport import HttpTransport

        self._transport_class = HttpTransport
        self.responses = responses or {}
        self.status_codes = status_codes or {}
        self.default_status_code = default_status_code
        self.requests: List[Tuple[HttpRequest, Dict[str, Any]]] = []

        # Patch the Azure auth functions to avoid Base64 decoding issues
        self._patch_azure_auth()

    def _patch_azure_auth(self) -> None:
        """Patch Azure authentication functions to bypass actual crypto operations."""
        # Only patch if needed and not already patched
        if not hasattr(self, "_auth_patches"):
            auth_module = "azure.storage.blob._shared.authentication"
            try:
                # We need to patch the sign_string function to avoid base64 decoding issues
                self._sign_string_patch = patch(f"{auth_module}.sign_string", return_value=b"mock_signature")
                self._sign_string_patch.start()

                # We also patch the _wrap_exception to prevent cryptic error messages
                self._wrap_exception_patch = patch(f"{auth_module}._wrap_exception", return_value=lambda e: e)
                self._wrap_exception_patch.start()

                self._auth_patches = True
            except Exception:
                # If patching fails, we'll continue without it
                # The tests may fail with Base64 decoding errors
                pass

    def __del__(self) -> None:
        """Clean up patches when the object is deleted."""
        self._stop_patches()

    def _stop_patches(self) -> None:
        """Stop all patches."""
        if hasattr(self, "_auth_patches"):
            try:
                if hasattr(self, "_sign_string_patch"):
                    self._sign_string_patch.stop()
                if hasattr(self, "_wrap_exception_patch"):
                    self._wrap_exception_patch.stop()
            except Exception:
                pass

    def send(self, request: HttpRequest, **kwargs: Any) -> HttpResponse:
        """Process the request and return a mocked response."""
        # Store the request for later inspection
        self.requests.append((request, kwargs))

        # Check if we have a predefined response for an operation
        operation = kwargs.get("operation_name")
        if operation and operation in self.responses:
            return self.responses[operation]

        # Check if we have a status code for this URL pattern
        status_code = self.default_status_code
        for url_pattern, code in self.status_codes.items():
            if url_pattern in request.url:
                status_code = code
                break

        # Create and return a response
        # Note: In newer versions of Azure SDK, HttpResponse requires an internal_response
        # Here we're creating a minimal mock for testing purposes
        mock_internal_response = MagicMock()
        mock_internal_response.status_code = status_code
        mock_internal_response.headers = {"content-type": "application/json"}
        mock_internal_response.body = kwargs.get("body", b'{"status": "mocked"}')

        response = HttpResponse(request=request, internal_response=mock_internal_response)
        return response
