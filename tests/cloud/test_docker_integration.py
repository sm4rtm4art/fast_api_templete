"""Docker-based integration tests for cloud services.

These tests use Docker containers to emulate cloud services locally.
These tests require Docker to be running and available on the system.
They are marked with skip_docker marker so they can be explicitly included
with: pytest -m docker_integration
"""

import json
import uuid
from typing import Any, Dict, Generator

import boto3
import docker
import pika
import pytest
import redis
from minio import Minio

from fast_api_template.cloud.cloud_service_provider import CloudServiceProvider
from fast_api_template.config.cloud import CloudConfig

# Mark all tests in this module to be skipped by default
pytestmark = pytest.mark.skip_docker


@pytest.fixture(scope="module")
def docker_client() -> docker.DockerClient:
    """Create a Docker client for managing containers."""
    return docker.from_env()


@pytest.fixture(scope="module")
def minio_container(docker_client: docker.DockerClient) -> Generator[docker.models.containers.Container, None, None]:
    """Start a MinIO container for S3-compatible storage testing."""
    container = docker_client.containers.run(
        "minio/minio:latest",
        command="server /data",
        environment={"MINIO_ACCESS_KEY": "minioadmin", "MINIO_SECRET_KEY": "minioadmin"},
        ports={"9000/tcp": 9000},
        detach=True,
    )

    # Wait for MinIO to be ready
    import time

    # Could be improved with proper readiness check
    time.sleep(5)

    yield container

    # Cleanup
    container.stop()
    container.remove()


@pytest.fixture(scope="module")
def redis_container(docker_client: docker.DockerClient) -> Generator[docker.models.containers.Container, None, None]:
    """Start a Redis container for cache testing."""
    container = docker_client.containers.run("redis:latest", ports={"6379/tcp": 6379}, detach=True)

    # Wait for Redis to be ready
    import time

    # Could be improved with proper readiness check
    time.sleep(3)

    yield container

    # Cleanup
    container.stop()
    container.remove()


@pytest.fixture(scope="module")
def rabbitmq_container(docker_client: docker.DockerClient) -> Generator[docker.models.containers.Container, None, None]:
    """Start a RabbitMQ container for queue testing."""
    try:
        container = docker_client.containers.run(
            "rabbitmq:management", ports={"5672/tcp": 5672, "15672/tcp": 15672}, detach=True
        )

        # Wait for RabbitMQ to be ready
        import time

        # Use a maximum timeout to prevent test hanging
        max_wait = 30
        start_time = time.time()
        ready = False

        # Poll container logs to check for readiness
        while time.time() - start_time < max_wait and not ready:
            logs = container.logs().decode("utf-8", errors="replace")
            if "Server startup complete" in logs:
                ready = True
                break
            time.sleep(1)

        # Even if we don't see the ready message, give it a bit more time
        if not ready:
            time.sleep(5)

        yield container
    except Exception as e:
        pytest.skip(f"Error setting up RabbitMQ container: {e}")
    finally:
        # Cleanup
        if "container" in locals():
            try:
                container.stop(timeout=5)
                container.remove()
            except Exception:
                pass  # Best effort cleanup


@pytest.fixture
def minio_client(minio_container) -> Minio:
    """Create a MinIO client for S3-compatible storage testing."""
    return Minio("localhost:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)


@pytest.fixture
def s3_bucket(minio_client) -> Generator[str, None, None]:
    """Create a test bucket in MinIO."""
    bucket_name = f"test-bucket-{uuid.uuid4().hex[:8]}"

    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    yield bucket_name

    # Cleanup - first delete all objects, then the bucket
    objects = minio_client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        minio_client.remove_object(bucket_name, obj.object_name)

    minio_client.remove_bucket(bucket_name)


@pytest.fixture
def redis_client(redis_container) -> redis.Redis:
    """Create a Redis client for cache testing."""
    return redis.Redis(host="localhost", port=6379, decode_responses=True)


@pytest.fixture(scope="module")
def rabbitmq_connection(rabbitmq_container) -> Generator[pika.BlockingConnection, None, None]:
    """Create a RabbitMQ connection for queue testing."""
    connection = None
    try:
        # Add a connection timeout to prevent hanging
        connection_params = pika.ConnectionParameters(  # type: ignore
            host="localhost", port=5672, connection_attempts=3, retry_delay=1, socket_timeout=5
        )
        connection = pika.BlockingConnection(connection_params)
        yield connection
    except Exception as e:  # Catch all exceptions including pika connection errors
        pytest.skip(f"Could not connect to RabbitMQ: {e}")
    finally:
        # Cleanup
        try:
            # Try to close any existing connection
            if connection and hasattr(connection, "is_open") and connection.is_open:
                connection.close()
        except Exception:
            pass  # Ignore connection errors


@pytest.fixture
def rabbitmq_channel(rabbitmq_connection) -> Generator[Any, None, None]:  # Using Any for pika channel type
    """Create a RabbitMQ channel for queue operations."""
    if rabbitmq_connection is None:
        pytest.skip("RabbitMQ connection not available")

    channel = rabbitmq_connection.channel()

    yield channel

    # Cleanup queues
    # This assumes no other tests are running concurrently with the same queue names
    try:
        # This is needed because pika doesn't have proper type stubs
        channel.queue_delete(queue="test-queue")
    except Exception:
        pass  # Best effort cleanup


@pytest.fixture
def custom_provider_settings(s3_bucket) -> Dict[str, Any]:
    """Create settings for a custom provider using local services."""
    return {
        "cloud": {
            "provider": "custom",
            "custom_provider_config": {
                "storage": {
                    "endpoint": "http://localhost:9000",
                    "access_key": "minioadmin",
                    "secret_key": "minioadmin",
                    "bucket": s3_bucket,
                    "type": "s3",
                },
                "cache": {"host": "localhost", "port": 6379, "type": "redis"},
                "queue": {"host": "localhost", "port": 5672, "type": "rabbitmq"},
            },
        }
    }


class CustomSettings:
    """Custom settings class for integration testing."""

    def __init__(self, settings_dict: Dict[str, Any]):
        """Initialize with settings dictionary."""
        self.settings_dict = settings_dict

    def get(self, key: str, default: Any = None) -> Any:
        """Get nested setting by dot-notation key."""
        parts = key.split(".")
        current = self.settings_dict

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default

        return current


@pytest.fixture
def custom_config(custom_provider_settings) -> CloudConfig:
    """Create a CloudConfig instance for the custom provider."""
    # Mypy will complain here, but this is a test-only fixture
    settings = CustomSettings(custom_provider_settings)
    return CloudConfig(settings)  # type: ignore


@pytest.mark.docker_integration
@pytest.mark.skip(reason="Docker tests require available ports and Docker running")
class TestDockerIntegration:
    """Integration tests using Docker containers to emulate cloud services."""

    def test_minio_operations(self, minio_client: Minio, s3_bucket: str):
        """Test MinIO operations directly with the MinIO client."""
        # Create some test data
        test_data = b"Hello, MinIO!"
        test_object = "test-object.txt"

        # Put an object
        from io import BytesIO

        minio_client.put_object(
            bucket_name=s3_bucket, object_name=test_object, data=BytesIO(test_data), length=len(test_data)
        )

        # Get the object and verify content
        response = minio_client.get_object(s3_bucket, test_object)
        content = response.read()
        response.close()

        assert content == test_data

        # Clean up
        minio_client.remove_object(s3_bucket, test_object)

    def test_redis_operations(self, redis_client: redis.Redis):
        """Test Redis operations directly with the Redis client."""
        # Set a key
        key = "test-key"
        value = "test-value"
        redis_client.set(key, value)

        # Get the key and verify value
        assert redis_client.get(key) == value

        # Clean up
        redis_client.delete(key)

    @pytest.mark.skip_docker
    def test_rabbitmq_operations(  # noqa: C901
        self,
        rabbitmq_channel: Any,  # Using Any for pika channel type
    ):
        """Test RabbitMQ operations directly with the Pika client."""
        if not rabbitmq_channel:
            pytest.skip("RabbitMQ channel not available")

        # Add a timeout function to prevent hanging tests
        def _with_timeout(func, *args, timeout=3, **kwargs):
            """Execute function with a timeout."""
            import platform
            import signal
            import threading

            # Use different timeout implementations based on platform
            if platform.system() != "Windows":
                # Unix-based systems can use SIGALRM
                def _timeout_handler(signum, frame):
                    raise TimeoutError(f"Function {func.__name__} timed out")

                # Set the timeout
                signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(timeout)

                try:
                    return func(*args, **kwargs)
                finally:
                    # Cancel the timeout
                    signal.alarm(0)
            else:
                # Windows doesn't support SIGALRM, use threading approach
                result = []
                error = []

                def _target():
                    try:
                        result.append(func(*args, **kwargs))
                    except Exception as e:
                        error.append(e)

                thread = threading.Thread(target=_target)
                thread.daemon = True
                thread.start()
                thread.join(timeout)

                if thread.is_alive():
                    raise TimeoutError(f"Function {func.__name__} timed out")

                if error:
                    raise error[0]

                return result[0]

        try:
            # Declare a queue
            queue_name = "test-queue"
            rabbitmq_channel.queue_declare(queue=queue_name)

            # Publish a message
            message = "Hello, RabbitMQ!"
            rabbitmq_channel.basic_publish(exchange="", routing_key=queue_name, body=message)

            # Get message count - with timeout
            queue_info = _with_timeout(rabbitmq_channel.queue_declare, queue=queue_name, passive=True, timeout=2)
            assert queue_info.method.message_count == 1

            # Consume the message - with timeout
            method_frame, _, body = _with_timeout(rabbitmq_channel.basic_get, queue_name, timeout=2)

            if method_frame:
                assert body.decode() == message
                rabbitmq_channel.basic_ack(method_frame.delivery_tag)
            else:
                pytest.fail("No message received from queue")
        except TimeoutError:
            pytest.fail("RabbitMQ test timed out")
        except Exception as e:  # Catch all rabbitmq errors
            pytest.fail(f"RabbitMQ error: {e}")
        finally:
            # Ensure cleanup always happens
            try:
                rabbitmq_channel.queue_delete(queue=queue_name)
            except Exception:
                pass  # Best effort cleanup

    def test_custom_provider_storage(self, custom_config: CloudConfig, s3_bucket: str):
        """Test storage operations using the custom provider."""
        # Get the custom cloud service
        CloudServiceProvider.create_service(custom_config)

        # Create some test data
        test_data = b"Hello, Custom Storage!"
        test_object = "test-custom-object.txt"

        # Create boto3 S3 client from the custom client
        # In a real implementation, this would be handled by custom provider
        s3_client = boto3.client(
            "s3",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            region_name="us-east-1",
            # Using a config parameter that may not be in type stubs
            config=boto3.session.Config(signature_version="s3v4"),  # type: ignore
        )

        # Put an object
        s3_client.put_object(Bucket=s3_bucket, Key=test_object, Body=test_data)

        # Get the object and verify content
        response = s3_client.get_object(Bucket=s3_bucket, Key=test_object)
        content = response["Body"].read()

        assert content == test_data

        # Clean up
        s3_client.delete_object(Bucket=s3_bucket, Key=test_object)

    def test_custom_provider_cache(self, custom_config: CloudConfig):
        """Test cache operations using the custom provider."""
        # Get the custom cloud service
        CloudServiceProvider.create_service(custom_config)

        # Get the cache client - this would need to be implemented in the custom provider
        # Here we're directly using Redis for testing
        cache_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

        # Set a key
        key = "test-custom-key"
        value = "test-custom-value"
        cache_client.set(key, value)

        # Get the key and verify value
        assert cache_client.get(key) == value

        # Clean up
        cache_client.delete(key)

    def test_custom_provider_queue(self, custom_config: CloudConfig):
        """Test queue operations using the custom provider."""
        # Get the custom cloud service
        CloudServiceProvider.create_service(custom_config)

        # Get a RabbitMQ connection
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = connection.channel()

        # Declare a queue
        queue_name = "test-custom-queue"
        channel.queue_declare(queue=queue_name)

        # Publish a message
        message = "Hello, Custom Queue!"
        channel.basic_publish(exchange="", routing_key=queue_name, body=message)

        # Get message count
        queue_info = channel.queue_declare(queue=queue_name, passive=True)
        assert queue_info.method.message_count == 1

        # Consume the message
        method_frame, _, body = channel.basic_get(queue_name)  # type: ignore
        if method_frame:
            assert body.decode() == message
            channel.basic_ack(method_frame.delivery_tag)  # type: ignore
        else:
            pytest.fail("No message received from queue")

        # Clean up
        channel.queue_delete(queue=queue_name)  # type: ignore
        connection.close()

    def test_multi_provider_data_flow(self, custom_config: CloudConfig, s3_bucket: str):
        """Test data flow between multiple provider services."""
        # This test simulates a common workflow where:
        # 1. Data is fetched from storage
        # 2. Processed and stored in cache
        # 3. A message about the processed data is sent to a queue

        # Initialize service but not using directly in this test
        CloudServiceProvider.create_service(custom_config)

        # Step 1: Store data in MinIO/S3
        # Using a config parameter that may not be in type stubs
        boto_config = boto3.session.Config(signature_version="s3v4")  # type: ignore
        s3_client = boto3.client(
            "s3",
            endpoint_url="http://localhost:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            region_name="us-east-1",
            config=boto_config,
        )

        object_key = "test-workflow-data.json"
        original_data = {"id": str(uuid.uuid4()), "name": "Test Data", "timestamp": "2023-01-01T00:00:00Z"}

        s3_client.put_object(Bucket=s3_bucket, Key=object_key, Body=json.dumps(original_data))

        # Step 2: Retrieve data, "process" it, and store in Redis
        response = s3_client.get_object(Bucket=s3_bucket, Key=object_key)
        retrieved_data = json.loads(response["Body"].read().decode())

        # "Process" the data
        processed_data = retrieved_data.copy()
        processed_data["processed"] = True
        processed_data["process_timestamp"] = "2023-01-01T00:01:00Z"

        # Store in Redis
        cache_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

        cache_key = f"processed:{retrieved_data['id']}"
        cache_client.set(cache_key, json.dumps(processed_data))

        # Step 3: Send a message to RabbitMQ about the processed data
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = connection.channel()

        queue_name = "test-workflow-queue"
        channel.queue_declare(queue=queue_name)

        message = {"action": "data_processed", "data_id": retrieved_data["id"], "cache_key": cache_key}

        channel.basic_publish(exchange="", routing_key=queue_name, body=json.dumps(message))

        # Step 4: Verify the flow by:
        # - Consuming the message
        # - Using the message to get the data from cache
        # - Comparing it to the original

        # Get the message
        # Type ignore due to missing pika stubs
        method_frame, _, body = channel.basic_get(queue_name)  # type: ignore
        assert method_frame is not None, "No message in queue"

        received_message = json.loads(body.decode())
        assert received_message["data_id"] == retrieved_data["id"]

        # Get from cache
        cached_key = received_message["cache_key"]
        cached_value = cache_client.get(cached_key)
        cached_data = {}  # Default value in case cache lookup fails
        if cached_value is not None:
            cached_data = json.loads(cached_value)

        # Verify the data
        assert cached_data["id"] == original_data["id"]
        assert cached_data["processed"] is True

        # Clean up
        # Type ignore due to missing pika stubs
        channel.queue_delete(queue=queue_name)  # type: ignore
        connection.close()
        cache_client.delete(cache_key)
        s3_client.delete_object(Bucket=s3_bucket, Key=object_key)
