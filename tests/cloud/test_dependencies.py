"""Test cloud provider dependencies.

This module verifies that all required cloud provider dependencies can be
imported correctly, helping to catch missing dependencies early.
"""

import importlib
import sys
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
    missing = []

    for module in modules:
        success, error = import_module(module)
        if not success:
            missing.append(f"{module} - {error}")

    if missing:
        pytest.fail(f"Missing or broken dependencies for {provider}: {', '.join(missing)}")


def test_cloud_service_imports() -> None:
    """Test that all cloud service implementations can be imported."""
    from fast_api_template.cloud import (
        AWSCloudService,
        AzureCloudService,
        CloudService,
        CloudServiceProvider,
        CustomCloudService,
        GCPCloudService,
        HetznerCloudService,
        LocalCloudService,
    )

    # Just verify the imports work, no assertions needed beyond this point
    assert issubclass(AWSCloudService, CloudService)
    assert issubclass(AzureCloudService, CloudService)
    assert issubclass(GCPCloudService, CloudService)
    assert issubclass(HetznerCloudService, CloudService)
    assert issubclass(CustomCloudService, CloudService)
    assert issubclass(LocalCloudService, CloudService)
    assert CloudServiceProvider is not None


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
        pytest.skip("Some cloud-test dependencies are missing. " "Install with: pip install -e '.[cloud-test]'")
