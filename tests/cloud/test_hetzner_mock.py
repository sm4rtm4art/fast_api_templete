"""Test Hetzner cloud services using requests_mock.

This module demonstrates how to mock Hetzner Cloud API responses
without requiring an external mock server.
"""

import pytest
import requests_mock

from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig


class TestSettings:
    """Mock settings for Hetzner testing."""
    
    def __init__(self):
        self._settings = {
            "cloud": {
                "provider": "hetzner",
                "region": "eu-central",
                "hetzner": {
                    "api_token": "test-api-token",
                    "datacenter": "fsn1",
                    "project_id": "test-project",
                    "storage": {
                        "box_id": "test-box-id",
                        "subdomain": "test-subdomain"
                    },
                    "cache": {
                        "host": "redis.example.com",
                        "port": 6379,
                        "password": "test-password"
                    },
                    "queue": {
                        "host": "rabbitmq.example.com",
                        "port": 5672,
                        "username": "test-user",
                        "password": "test-password"
                    }
                }
            }
        }
    
    def get(self, key, default=None):
        """Get nested setting by dot-notation key."""
        parts = key.split('.')
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
def hetzner_config():
    """Create Hetzner configuration for testing."""
    return CloudConfig(TestSettings())


class TestHetznerMock:
    """Test Hetzner cloud service using request_mock."""
    
    @pytest.fixture
    def hetzner_service(self, hetzner_config):
        """Create a Hetzner cloud service for testing."""
        return CloudServiceProvider.create_service(hetzner_config)
    
    def test_storage_client_creation(self, hetzner_service):
        """Test getting the Hetzner storage client."""
        # Get the storage client
        with requests_mock.Mocker() as m:
            # Mock Hetzner API endpoints
            m.get(
                'https://api.hetzner.cloud/v1/servers', 
                json={'servers': []}, 
                headers={'Content-Type': 'application/json'}
            )
            
            storage_client = hetzner_service.get_storage_client()
            
            # Verify correct headers are set
            auth = storage_client.headers['Authorization']
            assert auth == 'Bearer test-api-token'
            assert storage_client.headers['Content-Type'] == 'application/json'
    
    def test_server_operations(self, hetzner_service):
        """Test Hetzner server operations using requests_mock."""
        with requests_mock.Mocker() as m:
            # Mock server creation
            m.post(
                'https://api.hetzner.cloud/v1/servers', 
                json={
                    'server': {
                        'id': 42,
                        'name': 'test-server',
                        'status': 'running',
                        'created': '2019-01-08T12:10:00+00:00',
                        'server_type': {
                            'id': 1,
                            'name': 'cx11'
                        },
                        'datacenter': {
                            'id': 1,
                            'name': 'fsn1-dc14',
                            'location': {
                                'id': 1,
                                'name': 'fsn1'
                            }
                        },
                        'public_net': {
                            'ipv4': {
                                'ip': '1.2.3.4',
                                'blocked': False
                            },
                            'ipv6': {
                                'ip': '2001:db8::/64',
                                'blocked': False
                            }
                        }
                    }
                },
                status_code=201
            )
            
            # Mock server listing
            m.get(
                'https://api.hetzner.cloud/v1/servers',
                json={
                    'servers': [{
                        'id': 42,
                        'name': 'test-server',
                        'status': 'running'
                    }]
                }
            )
            
            # Mock server deletion
            m.delete(
                'https://api.hetzner.cloud/v1/servers/42',
                status_code=204
            )
            
            # Get the client
            client = hetzner_service.get_storage_client()
            
            # Create a server
            server_url = 'https://api.hetzner.cloud/v1/servers'
            response = client.post(
                server_url, 
                json={
                    'name': 'test-server',
                    'server_type': 'cx11',
                    'datacenter': 'fsn1-dc14',
                    'image': 'ubuntu-20.04'
                }
            )
            
            # Check for success
            assert response.status_code == 201
            data = response.json()
            assert data['server']['name'] == 'test-server'
            assert data['server']['id'] == 42
            
            # List servers
            response = client.get('https://api.hetzner.cloud/v1/servers')
            data = response.json()
            assert len(data['servers']) == 1
            assert data['servers'][0]['id'] == 42
            
            # Delete server
            response = client.delete('https://api.hetzner.cloud/v1/servers/42')
            assert response.status_code == 204
    
    def test_storage_box_operations(self, hetzner_service):
        """Test Hetzner Storage Box operations using requests_mock."""
        with requests_mock.Mocker() as m:
            # Mock Storage Box API (these are fictitious endpoints)
            storage_box_id = 'test-box-id'
            
            # Storage box URL templates
            storage_box_api = 'https://robot-ws.your-server.de/storagebox'
            storage_url = 'https://u123456.your-storagebox.de'
            
            # Mock getting Storage Box info
            m.get(
                f'{storage_box_api}/{storage_box_id}',
                json={
                    'id': storage_box_id,
                    'product': 'BX10',
                    'size': 1024 * 1024 * 1024 * 10,  # 10 GB
                    'status': 'ready'
                }
            )
            
            # Mock file upload
            test_file = f'{storage_url}/test-file.txt'
            m.put(test_file, status_code=201)
            
            # Mock file download
            m.get(
                test_file,
                text='Hello, Hetzner Storage Box!',
                status_code=200
            )
            
            # Mock file deletion
            m.delete(test_file, status_code=204)
            
            # Get the client
            client = hetzner_service.get_storage_client()
            
            # Simulate operations with the Storage Box
            # In a real implementation, this would use a specialized SDK
            # but for testing we're just simulating the HTTP requests
            
            # Get Storage Box info
            sb_url = f'{storage_box_api}/{storage_box_id}'
            response = client.get(sb_url)
            assert response.status_code == 200
            data = response.json()
            assert data['id'] == storage_box_id
            assert data['product'] == 'BX10'
            
            # Upload a file
            content = "Hello, Hetzner Storage Box!"
            response = client.put(test_file, data=content)
            assert response.status_code == 201
            
            # Download a file
            response = client.get(test_file)
            assert response.status_code == 200
            assert response.text == 'Hello, Hetzner Storage Box!'
            
            # Delete a file
            response = client.delete(test_file)
            assert response.status_code == 204 