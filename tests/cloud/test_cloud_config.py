"""Test the cloud configuration."""

import pytest

from fast_api_template.config.cloud import CloudConfig, CloudProvider


class MockSettings:
    """Mock settings for testing cloud configuration."""
    
    def __init__(self, settings_dict=None):
        self.settings_dict = settings_dict or {}
    
    def get(self, key, default=None):
        """Get a setting by key with default fallback."""
        parts = key.split('.')
        current = self.settings_dict
        
        for part in parts:
            if part not in current:
                return default
            current = current[part]
            
        return current


@pytest.fixture
def aws_settings():
    """Create AWS mock settings."""
    return MockSettings({
        'cloud': {
            'provider': 'aws',
            'region': 'us-west-2',
            'aws': {
                'profile': 'test-profile',
                'role_arn': 'arn:aws:iam::123456789012:role/test-role',
                's3': {
                    'bucket': 'test-bucket'
                },
                'elasticache': {
                    'endpoint': 'test.cache.amazonaws.com',
                    'port': 6379
                },
                'sqs': {
                    'queue_url': (
                        'https://sqs.us-west-2.amazonaws.com/'
                        '123456789012/test-queue'
                    )
                }
            }
        }
    })


@pytest.fixture
def gcp_settings():
    """Create GCP mock settings."""
    return MockSettings({
        'cloud': {
            'provider': 'gcp',
            'project_id': 'test-project',
            'region': 'us-central1',
            'gcp': {
                'credentials_path': '/path/to/credentials.json',
                'storage': {
                    'bucket': 'test-bucket'
                },
                'memorystore': {
                    'instance': 'test-instance',
                    'project_id': 'test-project'
                },
                'pubsub': {
                    'topic': 'test-topic',
                    'subscription': 'test-subscription'
                }
            }
        }
    })


@pytest.fixture
def azure_settings():
    """Create Azure mock settings."""
    return MockSettings({
        'cloud': {
            'provider': 'azure',
            'region': 'eastus',
            'tenant_id': 'test-tenant',
            'azure': {
                'subscription_id': 'test-subscription',
                'resource_group': 'test-resource-group',
                'storage': {
                    'container': 'test-container',
                    'account_name': 'teststorage'
                },
                'redis': {
                    'host': 'test-host',
                    'port': 6380
                },
                'servicebus': {
                    'namespace': 'test-namespace',
                    'queue': 'test-queue'
                }
            }
        }
    })


@pytest.fixture
def hetzner_settings():
    """Create Hetzner mock settings."""
    return MockSettings({
        'cloud': {
            'provider': 'hetzner',
            'region': 'eu-central',
            'hetzner': {
                'api_token': 'test-api-token',
                'datacenter': 'fsn1',
                'project_id': 'test-project',
                'storage': {
                    'box_id': 'test-box-id',
                    'subdomain': 'test-subdomain'
                },
                'cache': {
                    'host': 'redis.example.com',
                    'port': 6379,
                    'password': 'test-password'
                },
                'queue': {
                    'host': 'rabbitmq.example.com',
                    'port': 5672,
                    'username': 'test-user',
                    'password': 'test-password'
                }
            }
        }
    })


@pytest.fixture
def custom_settings():
    """Create custom provider mock settings."""
    return MockSettings({
        'cloud': {
            'provider': 'custom',
            'region': 'local',
            'custom': {
                'name': 'test-custom',
                'storage': {
                    'type': 'minio',
                    'endpoint': 'minio.local:9000',
                    'access_key': 'minioadmin',
                    'secret_key': 'minioadmin'
                },
                'cache': {
                    'type': 'redis',
                    'host': 'redis.local',
                    'port': 6379
                },
                'queue': {
                    'type': 'rabbitmq',
                    'host': 'rabbitmq.local'
                }
            }
        }
    })


def test_cloud_config_initialization(aws_settings):
    """Test basic initialization of CloudConfig."""
    config = CloudConfig(aws_settings)
    
    assert config.provider == CloudProvider.AWS
    assert config.region == 'us-west-2'
    assert config.project_id is None
    assert config.tenant_id is None


def test_is_cloud_property():
    """Test is_cloud property."""
    local_config = CloudConfig(MockSettings())
    aws_config = CloudConfig(MockSettings({'cloud': {'provider': 'aws'}}))
    
    assert local_config.is_cloud is False
    assert aws_config.is_cloud is True


def test_aws_config_property(aws_settings):
    """Test aws_config property."""
    config = CloudConfig(aws_settings)
    
    aws_config = config.aws_config
    assert aws_config is not None
    assert aws_config['region'] == 'us-west-2'
    assert aws_config['profile'] == 'test-profile'
    assert aws_config['role_arn'] == 'arn:aws:iam::123456789012:role/test-role'
    
    # Test non-AWS provider returns None
    local_config = CloudConfig(MockSettings())
    assert local_config.aws_config is None


def test_gcp_config_property(gcp_settings):
    """Test gcp_config property."""
    config = CloudConfig(gcp_settings)
    
    gcp_config = config.gcp_config
    assert gcp_config is not None
    assert gcp_config['project_id'] == 'test-project'
    assert gcp_config['region'] == 'us-central1'
    assert gcp_config['credentials_path'] == '/path/to/credentials.json'
    
    # Test non-GCP provider returns None
    local_config = CloudConfig(MockSettings())
    assert local_config.gcp_config is None


def test_azure_config_property(azure_settings):
    """Test azure_config property."""
    config = CloudConfig(azure_settings)
    
    azure_config = config.azure_config
    assert azure_config is not None
    assert azure_config['tenant_id'] == 'test-tenant'
    assert azure_config['subscription_id'] == 'test-subscription'
    assert azure_config['resource_group'] == 'test-resource-group'
    
    # Test non-Azure provider returns None
    local_config = CloudConfig(MockSettings())
    assert local_config.azure_config is None


def test_hetzner_config_property(hetzner_settings):
    """Test hetzner_config property."""
    config = CloudConfig(hetzner_settings)
    
    hetzner_config = config.hetzner_config
    assert hetzner_config is not None
    assert hetzner_config['api_token'] == 'test-api-token'
    assert hetzner_config['datacenter'] == 'fsn1'
    assert hetzner_config['project_id'] == 'test-project'
    
    # Test non-Hetzner provider returns None
    local_config = CloudConfig(MockSettings())
    assert local_config.hetzner_config is None


def test_custom_provider_config_property(custom_settings):
    """Test custom_provider_config property."""
    config = CloudConfig(custom_settings)
    
    custom_config = config.custom_provider_config
    assert custom_config is not None
    assert custom_config['name'] == 'test-custom'
    assert custom_config['storage']['type'] == 'minio'
    
    # Test non-custom provider returns None
    local_config = CloudConfig(MockSettings())
    assert local_config.custom_provider_config is None


def test_get_storage_config(aws_settings, gcp_settings, azure_settings):
    """Test get_storage_config method."""
    # Test AWS
    aws_config = CloudConfig(aws_settings)
    aws_storage = aws_config.get_storage_config()
    assert aws_storage['type'] == 's3'
    assert aws_storage['bucket'] == 'test-bucket'
    assert aws_storage['region'] == 'us-west-2'
    
    # Test GCP
    gcp_config = CloudConfig(gcp_settings)
    gcp_storage = gcp_config.get_storage_config()
    assert gcp_storage['type'] == 'gcs'
    assert gcp_storage['bucket'] == 'test-bucket'
    assert gcp_storage['project_id'] == 'test-project'
    
    # Test Azure
    azure_config = CloudConfig(azure_settings)
    azure_storage = azure_config.get_storage_config()
    assert azure_storage['type'] == 'azure'
    assert azure_storage['container'] == 'test-container'
    assert azure_storage['account_name'] == 'teststorage'
    
    # Test Local
    local_config = CloudConfig(MockSettings())
    local_storage = local_config.get_storage_config()
    assert local_storage['type'] == 'local'


def test_get_cache_config(aws_settings, gcp_settings, azure_settings):
    """Test get_cache_config method."""
    # Test AWS
    aws_config = CloudConfig(aws_settings)
    aws_cache = aws_config.get_cache_config()
    assert aws_cache['type'] == 'elasticache'
    assert aws_cache['endpoint'] == 'test.cache.amazonaws.com'
    assert aws_cache['port'] == 6379
    
    # Test GCP
    gcp_config = CloudConfig(gcp_settings)
    gcp_cache = gcp_config.get_cache_config()
    assert gcp_cache['type'] == 'memorystore'
    assert gcp_cache['instance'] == 'test-instance'
    assert gcp_cache['region'] == 'us-central1'
    
    # Test Azure
    azure_config = CloudConfig(azure_settings)
    azure_cache = azure_config.get_cache_config()
    assert azure_cache['type'] == 'cache'
    assert 'name' in azure_cache
    assert 'resource_group' in azure_cache
    
    # Test Local
    local_config = CloudConfig(MockSettings())
    local_cache = local_config.get_cache_config()
    assert local_cache['type'] == 'local'


def test_get_queue_config(aws_settings, gcp_settings, azure_settings):
    """Test get_queue_config method."""
    # Test AWS
    aws_config = CloudConfig(aws_settings)
    aws_queue = aws_config.get_queue_config()
    assert aws_queue['type'] == 'sqs'
    queue_url = 'https://sqs.us-west-2.amazonaws.com/123456789012/test-queue'
    assert aws_queue['queue_url'] == queue_url
    assert aws_queue['region'] == 'us-west-2'
    
    # Test GCP
    gcp_config = CloudConfig(gcp_settings)
    gcp_queue = gcp_config.get_queue_config()
    assert gcp_queue['type'] == 'pubsub'
    assert gcp_queue['topic'] == 'test-topic'
    assert gcp_queue['subscription'] == 'test-subscription'
    assert gcp_queue['project_id'] == 'test-project'
    
    # Test Azure
    azure_config = CloudConfig(azure_settings)
    azure_queue = azure_config.get_queue_config()
    assert azure_queue['type'] == 'servicebus'
    assert azure_queue['namespace'] == 'test-namespace'
    assert azure_queue['queue'] == 'test-queue'
    
    # Test Local
    local_config = CloudConfig(MockSettings())
    local_queue = local_config.get_queue_config()
    assert local_queue['type'] == 'local'


def test_get_storage_config_hetzner(hetzner_settings):
    """Test get_storage_config method for Hetzner provider."""
    config = CloudConfig(hetzner_settings)
    storage_config = config.get_storage_config()
    
    assert storage_config['type'] == 'hetzner'
    assert storage_config['storage_box'] == 'test-box-id'
    assert storage_config['datacenter'] == 'fsn1'
    assert storage_config['subdomain'] == 'test-subdomain'


def test_get_storage_config_custom(custom_settings):
    """Test get_storage_config method for custom provider."""
    config = CloudConfig(custom_settings)
    storage_config = config.get_storage_config()
    
    assert storage_config['type'] == 'minio'
    assert storage_config['endpoint'] == 'minio.local:9000'
    assert storage_config['access_key'] == 'minioadmin'
    assert storage_config['secret_key'] == 'minioadmin'


def test_get_cache_config_hetzner(hetzner_settings):
    """Test get_cache_config method for Hetzner provider."""
    config = CloudConfig(hetzner_settings)
    cache_config = config.get_cache_config()
    
    assert cache_config['type'] == 'redis'
    assert cache_config['host'] == 'redis.example.com'
    assert cache_config['port'] == 6379
    assert cache_config['password'] == 'test-password'


def test_get_cache_config_custom(custom_settings):
    """Test get_cache_config method for custom provider."""
    config = CloudConfig(custom_settings)
    cache_config = config.get_cache_config()
    
    assert cache_config['type'] == 'redis'
    assert cache_config['host'] == 'redis.local'
    assert cache_config['port'] == 6379


def test_get_queue_config_hetzner(hetzner_settings):
    """Test get_queue_config method for Hetzner provider."""
    config = CloudConfig(hetzner_settings)
    queue_config = config.get_queue_config()
    
    assert queue_config['type'] == 'rabbitmq'
    assert queue_config['host'] == 'rabbitmq.example.com'
    assert queue_config['port'] == 5672
    assert queue_config['username'] == 'test-user'
    assert queue_config['password'] == 'test-password'


def test_get_queue_config_custom(custom_settings):
    """Test get_queue_config method for custom provider."""
    config = CloudConfig(custom_settings)
    queue_config = config.get_queue_config()
    
    assert queue_config['type'] == 'rabbitmq'
    assert queue_config['host'] == 'rabbitmq.local' 