# Cloud Provider Testing

This directory contains tests for all supported cloud providers in the FastAPI template.

## Overview

We've implemented a comprehensive testing strategy that allows us to test cloud provider integrations without using actual cloud resources. This approach:

- Saves money (no cloud charges incurred)
- Enables tests to run in CI/CD with no cloud credentials
- Makes tests faster and more reliable
- Provides consistent test environments for all developers
- Allows offline development

## Testing Approach

Each cloud provider has its own testing approach:

| Provider           | Testing Approach           | Test File                      |
| ------------------ | -------------------------- | ------------------------------ |
| AWS                | Moto library               | `test_aws_moto.py`             |
| GCP                | Google's HttpMock          | `test_gcp_mock.py`             |
| Azure              | Standard unittest.mock     | `test_azure_mock.py`           |
| Hetzner            | requests_mock for HTTP API | `test_hetzner_mock.py`         |
| Custom/Local       | Docker containers          | `test_custom_provider_mock.py` |
| Docker Integration | Actual Docker containers   | `test_docker_integration.py`   |

## Directory Structure

- `conftest.py` - Common fixtures and utilities for cloud tests
- `test_cloud_base.py` - Abstract base classes for standardized cloud testing
- `test_cloud_config.py` - Tests for cloud configuration handling
- `test_cloud_service_provider.py` - Tests for the cloud service factory
- `test_dependencies.py` - Checks for required cloud dependencies
- `test_aws_moto.py` - AWS tests using Moto
- `test_azure_mock.py` - Azure tests using mocking
- `test_gcp_mock.py` - GCP tests using Google's HttpMock
- `test_hetzner_mock.py` - Hetzner tests using requests_mock
- `test_custom_provider_mock.py` - Tests for custom providers
- `test_docker_integration.py` - Integration tests using Docker containers

## Running Tests

To run the cloud tests, you need to install the cloud-test dependencies:

```bash
pip install -e ".[cloud-test]"
```

Then you can run specific test files:

```bash
# Run all cloud tests
pytest tests/cloud/

# Run only AWS tests
pytest tests/cloud/test_aws_moto.py

# Run GCP tests
pytest tests/cloud/test_gcp_mock.py
```

## Docker Integration Tests

Some tests use Docker containers to emulate cloud services locally. These tests require Docker to be installed and running:

```bash
# Run Docker-based integration tests
pytest tests/cloud/test_docker_integration.py
```

## Extending Cloud Tests

When adding a new cloud provider:

1. Create a new test file following the pattern `test_<provider>_mock.py`
2. Add fixtures to `conftest.py` if needed
3. Implement tests for all cloud service operations (storage, cache, queue)
4. Consider extending from `CloudServiceTestBase` in `test_cloud_base.py`
5. Add dependencies to `pyproject.toml` under `cloud-test`

## Documentation

For more details on the cloud testing strategy, refer to:

- `docs/testing/cloud_testing.md` for full documentation
- The docstrings in the test files for specific implementation details

## Azure

We use two approaches to mocking Azure services:

1. **Traditional mocking**: Using `unittest.mock` to patch Azure client classes and methods
2. **Transport-based mocking**: Using the Azure SDK's transport layer for more comprehensive mocking

### Traditional Mocking

The traditional approach involves patching the Azure client classes and their methods:

```python
from unittest.mock import MagicMock, patch

@patch('azure.storage.blob.BlobServiceClient')
def test_blob_storage(mock_blob_client_class):
    mock_blob_client = MagicMock()
    mock_container_client = MagicMock()
    mock_blob_client_class.from_connection_string.return_value = mock_blob_client
    mock_blob_client.get_container_client.return_value = mock_container_client

    # Test code using the mocked clients
```

This approach is simpler but has limitations when testing more complex scenarios.

### Transport-Based Mocking (Recommended)

The Azure SDK team officially recommends using a transport-based approach for mocking. This approach offers several advantages:

- **Realistic testing**: Tests the actual request/response flow, not just the API surface
- **Detailed verification**: Allows inspection of request payloads, headers, and URLs
- **Error simulation**: Makes it easy to simulate specific error responses
- **Cross-service consistency**: Works with all Azure SDK services that use the Azure Core transport

Our test framework provides two transport mock classes:

- `AzureMockTransport`: For synchronous clients
- `AzureAsyncMockTransport`: For asynchronous clients

Example usage:

```python
from azure.storage.blob import BlobServiceClient
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from tests.cloud.conftest import AzureMockTransport

# Create mock transport
mock_transport = AzureMockTransport(
    # Map URL patterns to status codes
    status_codes={
        "?restype=container": 201,  # Container operations return 201 Created
        "/non-existent-blob": 404,  # Return 404 for specific paths
    }
)

# Create custom responses for specific operations
mock_responses = {}
mock_responses["operation_name"] = HttpResponse(
    request=HttpRequest("GET", "https://example.com"),
    status_code=200,
    headers={"Content-Type": "application/json"},
    body=b'{"result": "success"}'
)
mock_transport.responses = mock_responses

# Create client with mock transport
blob_client = BlobServiceClient.from_connection_string(
    "DefaultEndpointsProtocol=https;AccountName=account;AccountKey=key;EndpointSuffix=core.windows.net",
    transport=mock_transport
)

# Now use the client - all HTTP requests will be intercepted
```

For complete examples, see `test_azure_transport_mock.py`.

## AWS

We use the Moto library for mocking AWS services, which provides a comprehensive set of mocks for the boto3 library. Our AWS testing strategy includes:

### Moto for AWS Service Mocking

Moto provides powerful decorator-based mocking for AWS services:

```python
from moto import mock_s3, mock_sqs

@mock_s3
def test_s3_operations():
    # Code using boto3 S3 client will use the Moto mock implementation
    s3_client = boto3.client('s3', region_name='us-west-2')
    s3_client.create_bucket(...)  # No actual AWS calls are made
```

### Test Data Management

We use a configurable `TestSettings` class for managing test configuration:

```python
class TestSettings:
    """Mock settings for AWS testing."""

    def __init__(self) -> None:
        self._settings: Dict[str, Any] = {
            "cloud": {
                "provider": "aws",
                "region": "us-west-2",
                # Additional settings...
            }
        }

    # Methods for getting/setting values

    def copy(self) -> 'TestSettings':
        """Create a copy of the settings object."""
        # Implementation to create independent copies
```

### Parameterized Testing

We use pytest.mark.parametrize for testing across multiple configurations:

```python
@pytest.mark.parametrize("region,bucket_name", [
    ("us-west-1", "test-bucket-west1"),
    ("us-east-1", "test-bucket-east1"),
    ("eu-west-1", "test-bucket-eu")
])
@mock_s3
def test_s3_multi_region(region, bucket_name):
    # Test S3 operations across multiple regions
```

### Dedicated Test Fixtures

We create specialized fixtures for pre-configured resources:

```python
@pytest.fixture
def aws_config_with_sqs_queue(aws_config):
    """Return a modified AWS config with SQS queue URL set."""
    # Create a test queue and return a configured CloudConfig
```

### Comprehensive Error Testing

We test both success and error scenarios:

```python
@mock_s3
def test_nonexistent_s3_object(aws_config):
    """Test handling of nonexistent S3 object."""
    # Implementation tests proper error handling
    with pytest.raises(s3_client.exceptions.NoSuchKey):
        # Attempt to access a nonexistent object
```

## Best Practices for Cloud Testing

Based on our experience implementing testing for multiple cloud providers, we've identified these best practices:

### General Best Practices

1. **Use Provider-Specific Mocking Approaches**

   - AWS: Use Moto library
   - Azure: Use transport-based mocking
   - GCP: Use HttpMock with JSON response templates
   - Hetzner: Use requests_mock

2. **Test Both Happy and Error Paths**

   - Verify successful operations
   - Test handling of not found errors
   - Test authentication/authorization failures
   - Test service limits and throttling

3. **Use Parameterized Testing**

   - Test with multiple regions/configurations
   - Test with different resource types and sizes
   - Avoid code duplication with parametrization

4. **Implement Reusable Test Fixtures**

   - Create fixtures for common resources
   - Use fixture composition for complex scenarios
   - Set appropriate scopes for performance

5. **Add Type Hints**
   - Add proper type annotations to test code
   - Improve maintainability and IDE support
   - Make use of typing.TypeVar for generic tests

### Provider-Specific Best Practices

1. **AWS (Moto)**

   - Use the appropriate decorator for each service
   - Be aware of region-specific behaviors
   - Clean up resources (though Moto handles this automatically)

2. **Azure (Transport Mocking)**

   - Use `AzureMockTransport` for HTTP-level testing
   - Create dedicated mock response factories
   - Add response logging for debugging

3. **GCP (HttpMock)**

   - Use standard response templates
   - Mock both success and error responses
   - Test pagination and batch operations

4. **Docker Integration**
   - Use shared containers where possible
   - Set appropriate container scopes
   - Implement proper cleanup

By following these practices, you can create a robust cloud testing strategy that is maintainable, efficient, and provides high confidence in your cloud integrations without incurring actual cloud costs.
