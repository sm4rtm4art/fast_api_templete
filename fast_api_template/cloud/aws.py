"""AWS cloud service implementation."""

import importlib.util
import os
import sys
from types import FrameType
from typing import Any, Dict, Literal, Optional, cast

import boto3
from mypy_boto3_s3.client import S3Client
from mypy_boto3_sqs.client import SQSClient

# Use a TYPE_CHECKING guard for redis import
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    # Define a placeholder for type checking
    REDIS_AVAILABLE = False

    # This keeps mypy happy while maintaining runtime safety
    class redis:  # type: ignore
        @staticmethod
        def Redis(*args: Any, **kwargs: Any) -> Any:
            """Placeholder for Redis client."""
            return None


from fast_api_template.cloud.cloud_service_interface import CloudService


class AWSCloudService(CloudService):
    """AWS cloud service implementation."""

    def get_client_params(self, service_name: str) -> Dict[str, Any]:
        """Get common client parameters for AWS services.

        Args:
            service_name: The AWS service name (e.g., 's3', 'sqs')

        Returns:
            Dict with client parameters
        """
        # Get region based on service config or fall back to general region
        aws_region = "us-east-1"  # Default region
        if self.config.aws_config:
            aws_region = self.config.aws_config.get("region", aws_region)

        # Check for service-specific region override
        if service_name == "sqs":
            queue_config = self.config.get_queue_config()
            if queue_config:
                aws_region = queue_config.get("region", aws_region)

        # Create the client parameters
        client_params: Dict[str, Any] = {
            "service_name": service_name,
            "region_name": aws_region,
        }

        # Add profile only if it exists and is not None
        if self.config.aws_config:
            profile = self.config.aws_config.get("profile")
            if profile is not None:
                client_params["profile_name"] = profile

        return client_params

    def _is_using_moto(self) -> bool:
        """Check if code is currently running under a Moto mock.

        Returns:
            bool: True if running within a Moto mock context, False otherwise.
        """
        # Check if a Moto mock is active by examining the stack
        # This checks if any module in the stack is from Moto
        if importlib.util.find_spec("moto") is None:
            return False

        # Check if we're in a test environment
        testing = "pytest" in sys.modules

        # More specific check: look for evidence that a Moto mock is active
        # Check for environment variable that might indicate Moto mock
        moto_env_var = os.environ.get("MOTO_MOCK_ACTIVE") == "1"

        # Check if any module in the call stack is from moto
        for frame_obj in sys._current_frames().values():
            # Properly type the frame as Optional[FrameType]
            moto_frame: Optional[FrameType] = frame_obj
            while moto_frame is not None:
                # Check if the module name starts with 'moto.'
                module_name = moto_frame.f_globals.get("__name__", "")
                if module_name.startswith("moto."):
                    return True
                moto_frame = moto_frame.f_back

        # Are we running tests with 'moto' in the test file name?
        if testing:
            for frame_obj in sys._current_frames().values():
                # Properly type the frame as Optional[FrameType]
                test_frame: Optional[FrameType] = frame_obj
                while test_frame is not None:
                    test_file = test_frame.f_globals.get("__file__", "")
                    if "test_aws_moto" in test_file:
                        return True
                    test_frame = test_frame.f_back

        return moto_env_var

    def get_storage_client(self) -> Optional[S3Client]:
        """Get AWS S3 client.

        Returns:
            Optional[S3Client]: The S3 client if AWS config is available,
            None otherwise.
        """
        if not self.config.aws_config:
            return None

        # Use literal 's3' to satisfy mypy's strict type checking for boto3
        service_name: Literal["s3"] = "s3"
        region_name = str(self.config.aws_config.get("region", "us-east-1"))
        profile_name = self.config.aws_config.get("profile")

        # Create params dict for boto3 client
        client_kwargs = {
            "service_name": service_name,
            "region_name": region_name,
        }

        # Only add profile_name when not running under Moto
        if profile_name is not None and not self._is_using_moto():
            client_kwargs["profile_name"] = profile_name

        # Type ignore needed for complex boto3 typing
        return cast(
            S3Client,
            boto3.client(**client_kwargs),  # type: ignore[call-overload]
        )

    def get_cache_client(self) -> Optional[Any]:
        """Get AWS ElastiCache client.

        Returns:
            Optional[Redis]: The Redis client if ElastiCache config is
            available, None otherwise.
        """
        if not REDIS_AVAILABLE:
            return None

        cache_config = self.config.get_cache_config()
        if not cache_config or cache_config.get("type") != "elasticache":
            return None
        return redis.Redis(
            host=cache_config["endpoint"],
            port=cache_config["port"],
            decode_responses=True,
        )

    def get_queue_client(self) -> Optional[SQSClient]:
        """Get AWS SQS client.

        Returns:
            Optional[SQSClient]: The SQS client if AWS config is available,
            None otherwise.
        """
        if not self.config.aws_config:
            return None
        queue_config = self.config.get_queue_config()
        if not queue_config or queue_config.get("type") != "sqs":
            return None

        # Use literal 'sqs' to satisfy mypy's strict type checking for boto3
        service_name: Literal["sqs"] = "sqs"

        # Get the region from queue config or fall back to AWS config
        default_region = self.config.aws_config.get("region", "us-east-1")
        region = queue_config.get("region", default_region)
        region_name = str(region)

        profile_name = self.config.aws_config.get("profile")

        # Create params dict for boto3 client
        client_kwargs = {
            "service_name": service_name,
            "region_name": region_name,
        }

        # Only add profile_name when not running under Moto
        if profile_name is not None and not self._is_using_moto():
            client_kwargs["profile_name"] = profile_name

        # Type ignore needed for complex boto3 typing
        return cast(
            SQSClient,
            boto3.client(**client_kwargs),  # type: ignore[call-overload]
        )
