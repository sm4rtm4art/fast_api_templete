"""Test Hetzner Cloud service implementation."""

import pytest
from unittest.mock import MagicMock, patch

from fast_api_template.cloud.hetzner import HetznerCloudService
from fast_api_template.config.cloud import CloudConfig


class TestHetznerCloudService:
    """Test suite for Hetzner Cloud service."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config for Hetzner."""
        config = MagicMock(spec=CloudConfig)
        config.provider = 'hetzner'
        
        # Mock the hetzner_config property
        hetzner_config = {
            'api_token': 'test-api-token',
            'datacenter': 'fsn1',
            'project_id': 'test-project'
        }
        config.hetzner_config = hetzner_config
        
        return config
    
    @patch('requests.Session')
    def test_get_storage_client(self, mock_session, mock_config):
        """Test getting Hetzner Storage Box client."""
        # Setup
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        
        # Execute
        service = HetznerCloudService(mock_config)
        client = service.get_storage_client()
        
        # Verify
        assert client is mock_session_instance
        mock_session_instance.headers.update.assert_called_once_with({
            'Authorization': 'Bearer test-api-token',
            'Content-Type': 'application/json'
        })
    
    def test_get_storage_client_no_token(self, mock_config):
        """Test getting storage client with no API token."""
        # Setup
        mock_config.hetzner_config = {'datacenter': 'fsn1'}
        
        # Execute
        service = HetznerCloudService(mock_config)
        client = service.get_storage_client()
        
        # Verify
        assert client is None
    
    def test_get_cache_client(self, mock_config):
        """Test getting cache client."""
        # Execute
        service = HetznerCloudService(mock_config)
        client = service.get_cache_client()
        
        # Verify - Hetzner doesn't have a managed Redis service
        assert client is None
    
    def test_get_queue_client(self, mock_config):
        """Test getting queue client."""
        # Execute
        service = HetznerCloudService(mock_config)
        client = service.get_queue_client()
        
        # Verify - Hetzner doesn't have a managed message queue service
        assert client is None 