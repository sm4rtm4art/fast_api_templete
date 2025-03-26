# Whitelist for vulture false positives

# Test mock attributes
from tests.cloud.test_custom_provider_mock import TestCustomProviderMock
mock = TestCustomProviderMock()
mock.return_value
mock.return_value.__call__()

# Test settings classes
class TestSettings:
    def __init__(self):
        pass
    def get(self, key, default=None):
        pass
    def as_dict(self):
        pass

# Mock variables
mock_method = None
mock_props = None
mock_body = None

# Fixture-related functions
def azure_config():
    pass

def custom_config():
    pass

def hetzner_config():
    pass 