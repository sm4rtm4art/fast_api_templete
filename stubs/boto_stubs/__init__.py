"""Type stubs for AWS testing."""

from typing import Any, Dict, List, TypedDict


class MessageTypeDef(TypedDict, total=False):
    """Message type definition for SQS."""
    MessageId: str
    ReceiptHandle: str
    MD5OfBody: str
    Body: str
    Attributes: Dict[str, str]
    MD5OfMessageAttributes: str
    MessageAttributes: Dict[str, Any]


class SQSResponseTypeDef(TypedDict, total=False):
    """Base response type for SQS operations."""
    Messages: List[MessageTypeDef]
    ResponseMetadata: Dict[str, Any]
    QueueUrl: str


class S3ResponseTypeDef(TypedDict, total=False):
    """Base response type for S3 operations."""
    Body: Any
    Buckets: List[Dict[str, str]]
    ResponseMetadata: Dict[str, Any]


class ClientExceptions:
    """Mock exceptions for AWS clients."""
    
    class NoSuchKey(Exception):
        """Exception for no such key."""
        pass
    
    class NoSuchBucket(Exception):
        """Exception for no such bucket."""
        pass 