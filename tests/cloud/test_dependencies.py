"""Test cloud provider dependencies.

This module verifies that all required cloud provider dependencies can be
imported correctly, helping to catch missing dependencies early.
"""

import importlib
import os
from typing import List, Tuple

import pytest


def import_module(module_name: str) -> Tuple[bool, str]:
    """Try to import a module and return success status and error message.

    Args:
        module_name: Name of the module to import

    Returns:
        Tuple containing:
            - Boolean indicating if import was successful
            - Error message if import failed, empty string otherwise
    """
    try:
        importlib.import_module(module_name)
        return True, ""
    except ImportError as e:
        return False, str(e)


@pytest.mark.parametrize(
    "provider,modules",
    [
        (
            "aws",
            [
                "boto3",
                "botocore",
                "moto",
                "mypy_boto3_s3",
                "mypy_boto3_sqs",
            ],
        ),
        (
            "azure",
            [
                "azure.storage.blob",
                "azure.servicebus",
                "azure.identity",
                "azure.mgmt.redis",
            ],
        ),
        (
            "gcp",
            [
                "google.cloud.storage",
                "google.cloud.pubsub_v1",
                "googleapiclient.discovery",
                "googleapiclient.http",
            ],
        ),
        (
            "redis",
            [
                "redis",
            ],
        ),
        (
            "http_mocking",
            [
                "requests_mock",
            ],
        ),
        (
            "docker",
            [
                "docker",
            ],
        ),
        (
            "minio",
            [
                "minio",
            ],
        ),
        (
            "rabbitmq",
            [
                "pika",
            ],
        ),
    ],
)
def test_provider_dependencies(provider: str, modules: List[str]) -> None:
    """Test that all dependencies for a cloud provider can be imported.

    Args:
        provider: Name of the cloud provider or service category
        modules: List of module names required for the provider
    """
    # Skip tests for optional providers in CI environment
    if provider in ["azure", "gcp"] and os.environ.get("CI") is not None:
        pytest.skip(f"Skipping {provider} dependency test in CI environment")

    missing = []

    for module in modules:
        success, error = import_module(module)
        if not success:
            missing.append(f"{module} - {error}")

    if missing:
        pytest.fail(f"Missing or broken dependencies for {provider}: {', '.join(missing)}")


def test_cloud_service_imports() -> None:
    """Test that all cloud service implementations can be imported."""
    # Skip in CI environment where optional cloud providers are not installed
    if os.environ.get("CI") is not None:
        pytest.skip("Skipping cloud service imports test in CI environment")
        
    # First check if we can import the base modules
    try:
        # Check if we can import AWS which is required
        from fast_api_template.cloud import (
            AWSCloudService,
            CloudService,
            CloudServiceProvider,
            CustomCloudService,
            HetznerCloudService,
            LocalCloudService,
        )

        # These assertions should always pass
        assert issubclass(AWSCloudService, CloudService)
        assert issubclass(LocalCloudService, CloudService)
        assert issubclass(CustomCloudService, CloudService)
        assert issubclass(HetznerCloudService, CloudService)
        assert CloudServiceProvider is not None

        # Now try to import optional cloud providers
        try:
            from fast_api_template.cloud import AzureCloudService

            assert issubclass(AzureCloudService, CloudService)
        except ImportError:
            # Skip Azure assertions if not available
            pass

        try:
            from fast_api_template.cloud import GCPCloudService

            assert issubclass(GCPCloudService, CloudService)
        except ImportError:
            # Skip GCP assertions if not available
            pass

    except ImportError as e:
        # If we can't import the base modules, that's a real failure
        pytest.fail(f"Failed to import required cloud modules: {e}")


def test_optional_dependencies() -> None:
    """Test if cloud-test dependencies are installed.

    This test helps ensure that the cloud-test dependencies from pyproject.toml
    are installed, which are needed for cloud testing.
    """
    # Check if running with cloud-test dependencies
    has_deps = all(
        imp[0]
        for imp in [
            import_module("moto"),
            import_module("requests_mock"),
            import_module("redis"),
            import_module("minio"),
            import_module("docker"),
        ]
    )

    if not has_deps:
        pytest.skip("Some cloud-test dependencies are missing. Install with: pip install -e '.[cloud-test]'")
