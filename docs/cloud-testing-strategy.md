# Cloud Provider Testing Strategy

This document outlines the comprehensive testing strategy for cloud providers in the FastAPI Template project.

## Testing Layers

Our cloud testing strategy follows a multi-layered approach to ensure both correctness and reliability:

1. **Unit Tests**: Test individual components in isolation with mocked dependencies
2. **Integration Tests**: Test interactions between components with minimal mocking
3. **Docker-based Integration Tests**: Test against real cloud-like services running in Docker
4. **End-to-End Tests**: Tests against actual cloud providers (optional and environment-dependent)

## Test Categories

### Unit Tests

Unit tests validate that individual cloud provider implementations function correctly with mocked dependencies:

- `test_cloud_config.py`: Tests the configuration management for all cloud providers
- `test_cloud_service_provider.py`: Tests the factory that creates appropriate service instances
- `test_aws_cloud_service.py`: Tests the AWS cloud service implementation
- `test_gcp_cloud_service.py`: Tests the GCP cloud service implementation
- `test_azure_cloud_service.py`: Tests the Azure cloud service implementation
- `test_hetzner_cloud_service.py`: Tests the Hetzner cloud service implementation
- `test_custom_cloud_service.py`: Tests the custom/local cloud service implementation

### Integration Tests

Integration tests validate that the cloud provider components work together as expected:

- `test_integration.py`: Tests the interactions between configuration, factory, and service implementations with minimal mocking

### Docker-based Integration Tests

These tests use Docker containers to provide real service implementations for thorough testing:

- `test_docker_integration.py`: Tests against actual cloud-like services (MinIO, Redis, etc.) running in Docker

## Testing Environment Features

### Fixtures and Helpers

- `conftest.py`: Provides shared fixtures and test utilities
- `MockSettings`: A helper class that simulates the Dynaconf settings interface
- `DockerServiceManager`: Manages Docker containers for integration testing

### Test Markers

Special pytest markers are used to categorize tests:

- `@pytest.mark.unit`: Unit tests (default)
- `@pytest.mark.integration`: Tests that validate component interaction
- `@pytest.mark.docker`: Tests that require Docker to be running
- `@pytest.mark.cloud`: Tests that require actual cloud provider credentials

## Running the Tests

### Basic Test Run

```bash
# Run all cloud provider tests
pytest tests/cloud/

# Run only unit tests
pytest tests/cloud/ -m "not integration and not docker and not cloud"

# Run integration tests
pytest tests/cloud/ -m "integration"

# Run Docker-based tests
pytest tests/cloud/ -m "docker"
```

### Environment Variables for Cloud Tests

To run tests against actual cloud providers, set the following environment variables:

#### AWS

```
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-west-2
```

#### GCP

```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_CLOUD_PROJECT=your-project-id
```

#### Azure

```
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

#### Hetzner

```
HETZNER_API_TOKEN=your-api-token
```

#### Custom/Local

```
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

## Test Coverage Goals

Our goal is to maintain at least 85% code coverage for the cloud provider implementations, with particular focus on:

1. Configuration handling and validation
2. Service client initialization
3. Error handling and fallback mechanisms
4. Environment variable processing

## Mocking Strategy

We use a tiered mocking approach:

1. **Deep Mocking**: Unit tests mock all external dependencies
2. **Partial Mocking**: Integration tests only mock cloud provider APIs
3. **Minimal Mocking**: Docker tests use real services with minimal or no mocking
4. **No Mocking**: Cloud tests connect to actual cloud providers (when credentials are available)

## CI/CD Integration

In CI/CD pipelines:

1. All unit and integration tests run on every PR and commit
2. Docker-based tests run only on specific branches or tags
3. Actual cloud provider tests run only when explicitly triggered and credentials are provided

## Test Data Management

Test data is managed systematically:

1. Test fixtures provide consistent test data
2. Docker containers are configured with predictable initial state
3. All tests clean up after themselves to prevent test pollution
4. Resource names include random components to prevent collisions in parallel test runs
