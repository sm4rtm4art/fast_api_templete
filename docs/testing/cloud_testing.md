# Cloud Provider Testing Strategy

This document outlines our approach to testing cloud provider integrations without using actual cloud resources, which helps save costs and enables running tests in CI/CD environments without cloud credentials.

## Overview

Our testing strategy for cloud providers follows these key principles:

1. **Cost Efficiency**: We don't run tests against actual cloud services, avoiding any charges.
2. **Speed**: Tests run quickly without network delays or API rate limits.
3. **Determinism**: Tests produce consistent results regardless of external cloud status.
4. **Offline Capability**: Developers can run tests without internet access.
5. **Realism**: Tests verify actual functionality, not just HTTP status codes.

## Testing Approaches by Provider

### AWS Testing with Moto

We use the [Moto](https://github.com/spulec/moto) library to mock AWS services.

```python
from moto import mock_s3, mock_sqs

@mock_s3
def test_s3_operations():
    # Test code here - Moto intercepts AWS API calls
    s3_client = boto3.client("s3", region_name="us-west-2")
    # Operations against this client use Moto's in-memory implementation
```

Key benefits of Moto:

- Comprehensive mocking of most AWS services
- Deep behavior implementation (not just API responses)
- Support for complex workflows (e.g., S3 triggers to Lambda)

### Google Cloud Platform (GCP) Testing

We use Google's official approach with `HttpMock` and `HttpMockSequence`:

```python
from googleapiclient.http import HttpMock, HttpMockSequence

def test_gcp_storage():
    # Create mock responses for API calls
    mock_responses = HttpMockSequence([
        ({'status': '200'}, json.dumps({'items': []})),  # Bucket list
        ({'status': '200'}, json.dumps({'name': 'test-bucket'}))  # Bucket creation
    ])

    # Patch the discovery build to use our mock
    with patch('googleapiclient.discovery.build') as mock_build:
        # Test code here
```

### Azure Testing

We use standard Python mocking techniques for Azure:

```python
from unittest.mock import MagicMock, patch

@patch('azure.storage.blob.BlobServiceClient')
def test_blob_storage(mock_blob_client_class):
    # Setup mock responses
    mock_blob_client = MagicMock()
    mock_blob_client_class.from_connection_string.return_value = mock_blob_client

    # Test code here using mock_blob_client
```

### Transport-Based Azure Mocking

The Azure SDK team recommends using a transport-based mocking approach for more comprehensive testing. This approach allows you to:

- Mock the actual HTTP requests and responses at the transport layer
- Inspect request parameters and headers sent to Azure services
- Simulate error responses and edge cases
- Share mock implementations across different Azure services

Our framework provides `AzureMockTransport` and `AzureAsyncMockTransport` classes:

```python
from azure.storage.blob import BlobServiceClient
from azure.core.pipeline.transport import HttpRequest, HttpResponse
from tests.cloud.conftest import AzureMockTransport

# Create a mock transport
mock_transport = AzureMockTransport(status_codes={
    "?restype=container": 201,  # Container creation succeeds
    "/nonexistent": 404,        # Simulate not found for specific paths
})

# Create a client with the mock transport
blob_client = BlobServiceClient.from_connection_string(
    "connection-string",
    transport=mock_transport
)

# Use the client in tests - all HTTP requests will be intercepted
container = blob_client.create_container("test-container")
```

For more precise control over responses, you can define specific HTTP responses:

```python
# Define specific HTTP responses for operations
mock_responses = {}
mock_responses["create_container"] = HttpResponse(
    request=HttpRequest("PUT", "https://account.blob.core.windows.net/container"),
    status_code=201,
    headers={"ETag": "0x8DA1E5CA36F2E75"},
)

# Set the responses on the transport
mock_transport.responses = mock_responses
```

We recommend using this transport-based approach for comprehensive testing of Azure services as it follows the official Azure SDK team recommendations.

### Hetzner Cloud Testing

We use `requests_mock` to intercept HTTP calls to Hetzner's API:

```python
import requests_mock

def test_hetzner_api():
    with requests_mock.Mocker() as m:
        # Mock API responses
        m.get('https://api.hetzner.cloud/v1/servers', json={'servers': []})

        # Test code here
```

### Custom/Local Provider Testing

For local services like Redis, MinIO, or RabbitMQ, we test with Docker containers:

```python
@pytest.fixture(scope="module")
def redis_container():
    container = docker_client.containers.run(
        "redis:latest",
        ports={"6379/tcp": 6379},
        detach=True
    )

    yield container

    container.stop()
    container.remove()
```

## Multi-Provider Integration Testing

We also test the flow of data between different provider services using Docker containers. This simulates realistic scenarios like:

1. Storing data in object storage
2. Processing and caching results
3. Sending notifications via message queues

These tests verify our cloud abstraction layer works correctly with different providers and services.

## Running Cloud Tests

### Prerequisites

- Docker installed and running (for integration tests)
- Python dependencies installed: `pip install -e ".[cloud-test]"`

### Running Tests

Run specific cloud provider tests:

```bash
# AWS tests
pytest tests/cloud/test_aws_moto.py

# GCP tests
pytest tests/cloud/test_gcp_mock.py

# Azure tests
pytest tests/cloud/test_azure_mock.py

# All cloud tests
pytest tests/cloud/
```

### CI/CD Integration

The cloud tests run in CI/CD environments without requiring cloud credentials. The test fixtures automatically set up the necessary mocks and Docker containers.

## Adding New Cloud Provider Tests

When adding tests for a new cloud provider:

1. Choose an appropriate mocking strategy (mock libraries, HTTP mocking, etc.)
2. Add necessary dependencies to `pyproject.toml` under `[project.optional-dependencies.cloud-test]`
3. Create test fixtures in `tests/cloud/conftest.py`
4. Create a test file following the pattern `test_<provider>_mock.py`
5. Implement tests for storage, cache, and queue operations

## Best Practices

- Test both success and error scenarios
- Verify data integrity, not just status codes
- Keep mock responses realistic
- Test service interactions, not just individual API calls
- Use appropriate scopes for fixtures to optimize test performance
