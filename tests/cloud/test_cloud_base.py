"""Base test class for standardized cloud testing.

This module provides abstract base classes for testing cloud service
implementations consistently across different providers.
"""

import abc
from typing import Any, Dict, List, Optional, Tuple

import pytest

from fast_api_template.cloud.cloud_service_interface import CloudService
from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig


class CloudServiceTestBase(abc.ABC):
    """Abstract base class for testing cloud services.

    This provides a standard set of test cases that should be implemented
    for each cloud provider to ensure consistent behavior across providers.
    
    Subclasses must implement the abstract methods and can add
    provider-specific tests.
    """

    @pytest.fixture
    @abc.abstractmethod
    def cloud_config(self) -> CloudConfig:
        """Create a cloud configuration for testing.
        
        Returns:
            CloudConfig: A configuration object for the cloud provider
        """
        pass
    
    @pytest.fixture
    def cloud_service(self, cloud_config) -> CloudService:
        """Create a cloud service instance for testing.
        
        Args:
            cloud_config: The cloud configuration fixture
            
        Returns:
            CloudService: An instance of the appropriate cloud service
        """
        return CloudServiceProvider.create_service(cloud_config)
    
    @abc.abstractmethod
    def test_storage_operations(self, cloud_service: CloudService) -> None:
        """Test storage operations for the cloud provider.
        
        At minimum, this should test:
        - Creating a storage resource (bucket, container, etc.)
        - Uploading an object/blob
        - Downloading the object/blob
        - Verifying the content
        - Deleting the object/blob
        - Cleaning up the storage resource
        
        Args:
            cloud_service: The cloud service instance
        """
        pass
    
    @abc.abstractmethod
    def test_cache_operations(self, cloud_service: CloudService) -> None:
        """Test cache operations for the cloud provider.
        
        At minimum, this should test:
        - Setting a cache key
        - Getting a cache key
        - Verifying cache expiration (if applicable)
        - Deleting a cache key
        
        Args:
            cloud_service: The cloud service instance
        """
        pass
    
    @abc.abstractmethod
    def test_queue_operations(self, cloud_service: CloudService) -> None:
        """Test queue operations for the cloud provider.
        
        At minimum, this should test:
        - Creating a queue (if applicable)
        - Sending a message
        - Receiving a message
        - Verifying the message content
        - Acknowledging/deleting the message
        - Cleaning up the queue
        
        Args:
            cloud_service: The cloud service instance
        """
        pass
    
    def test_client_initialization(self, cloud_service: CloudService) -> None:
        """Test that all clients can be initialized.
        
        This tests that:
        - Storage client can be created
        - Cache client can be created
        - Queue client can be created
        
        Args:
            cloud_service: The cloud service instance
        """
        storage_client = cloud_service.get_storage_client()
        cache_client = cloud_service.get_cache_client()
        queue_client = cloud_service.get_queue_client()
        
        # The availability of specific clients depends on the provider configuration
        # Some tests may not require all clients


class CloudServiceErrorTestBase(abc.ABC):
    """Abstract base class for testing cloud service error handling.
    
    This provides standard tests for error cases when using cloud services.
    Subclasses should implement the abstract methods to test provider-specific
    error handling.
    """
    
    @pytest.fixture
    @abc.abstractmethod
    def invalid_cloud_config(self) -> CloudConfig:
        """Create an invalid cloud configuration for testing errors.
        
        Returns:
            CloudConfig: An intentionally invalid configuration
        """
        pass
    
    @pytest.fixture
    def error_cloud_service(self, invalid_cloud_config) -> CloudService:
        """Create a cloud service with invalid configuration.
        
        Args:
            invalid_cloud_config: The invalid cloud configuration fixture
            
        Returns:
            CloudService: An instance with invalid configuration
        """
        return CloudServiceProvider.create_service(invalid_cloud_config)
    
    @abc.abstractmethod
    def test_storage_client_error(self, error_cloud_service: CloudService) -> None:
        """Test error handling for storage client operations.
        
        Args:
            error_cloud_service: Cloud service with invalid configuration
        """
        pass
    
    @abc.abstractmethod
    def test_cache_client_error(self, error_cloud_service: CloudService) -> None:
        """Test error handling for cache client operations.
        
        Args:
            error_cloud_service: Cloud service with invalid configuration
        """
        pass
    
    @abc.abstractmethod
    def test_queue_client_error(self, error_cloud_service: CloudService) -> None:
        """Test error handling for queue client operations.
        
        Args:
            error_cloud_service: Cloud service with invalid configuration
        """
        pass 