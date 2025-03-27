"""Type stub for minio.error module."""

from typing import Any, Optional

class S3Error(Exception):
    """Base exception for all minio S3 errors.

    This exception is raised for all S3 API errors.
    """

    def __init__(
        self,
        code: str,
        message: str,
        resource: Optional[str] = None,
        request_id: Optional[str] = None,
        host_id: Optional[str] = None,
        response: Optional[Any] = None,
    ) -> None:
        """Initialize S3Error with error details."""
        ...

    code: str
    message: str
    resource: Optional[str]
    request_id: Optional[str]
    host_id: Optional[str]
    response: Optional[Any]

class InvalidResponseError(S3Error):
    """Raised when the server returns an invalid response."""

    ...

class NoSuchBucket(S3Error):
    """Raised when the specified bucket does not exist."""

    ...

class NoSuchKey(S3Error):
    """Raised when the specified object key does not exist."""

    ...
