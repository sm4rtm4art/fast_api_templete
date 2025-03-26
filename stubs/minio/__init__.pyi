from typing import Any, Dict, Optional

class Minio:
    """Stub for the Minio S3 Client."""

    def __init__(
        self,
        endpoint: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        session_token: Optional[str] = None,
        secure: bool = True,
        region: Optional[str] = None,
        http_client: Optional[Any] = None,
        credentials: Optional[Any] = None,
    ) -> None: ...
    def make_bucket(self, bucket_name: str, location: Optional[str] = None) -> None: ...
    def bucket_exists(self, bucket_name: str) -> bool: ...
    def put_object(
        self,
        bucket_name: str,
        object_name: str,
        data: Any,
        length: Optional[int] = None,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]: ...
    def get_object(self, bucket_name: str, object_name: str) -> Any: ...
    def remove_object(self, bucket_name: str, object_name: str) -> None: ...
