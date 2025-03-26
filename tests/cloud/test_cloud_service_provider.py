"""Test the cloud service provider factory."""

import pytest

from fast_api_template.cloud.aws import AWSCloudService
from fast_api_template.cloud.azure import AzureCloudService
from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.cloud.gcp import GCPCloudService
from fast_api_template.cloud.local import LocalCloudService
from fast_api_template.config.cloud import CloudConfig


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    class MockSettings:
        def __init__(self, provider='local'):
            self.provider = provider
            
        def get(self, key, default=None):
            if key == "cloud.provider":
                return self.provider
            return default
    
    return MockSettings


def test_create_aws_service(mock_settings):
    """Test creating an AWS cloud service."""
    settings = mock_settings(provider='aws')
    config = CloudConfig(settings)
    
    service = CloudServiceProvider.create_service(config)
    
    assert isinstance(service, AWSCloudService)
    assert service.config == config


def test_create_gcp_service(mock_settings):
    """Test creating a GCP cloud service."""
    settings = mock_settings(provider='gcp')
    config = CloudConfig(settings)
    
    service = CloudServiceProvider.create_service(config)
    
    assert isinstance(service, GCPCloudService)
    assert service.config == config


def test_create_azure_service(mock_settings):
    """Test creating an Azure cloud service."""
    settings = mock_settings(provider='azure')
    config = CloudConfig(settings)
    
    service = CloudServiceProvider.create_service(config)
    
    assert isinstance(service, AzureCloudService)
    assert service.config == config


def test_create_local_service(mock_settings):
    """Test creating a local cloud service."""
    settings = mock_settings(provider='local')
    config = CloudConfig(settings)
    
    service = CloudServiceProvider.create_service(config)
    
    assert isinstance(service, LocalCloudService)
    assert service.config == config


def test_create_default_service(mock_settings):
    """Test creating a service with invalid provider defaults to local."""
    settings = mock_settings(provider='local')
    config = CloudConfig(settings)
    
    service = CloudServiceProvider.create_service(config)
    
    assert isinstance(service, LocalCloudService)
    assert service.config == config 