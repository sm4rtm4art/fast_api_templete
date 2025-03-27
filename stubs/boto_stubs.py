"""Type definitions for AWS boto3 responses.

This module defines common response type for AWS services used in the application.
"""

from typing import Any, Dict, List, Optional, TypedDict


class S3ObjectTypeDef(TypedDict, total=False):
    """Type definition for S3 Object metadata."""

    Key: str
    LastModified: str
    ETag: str
    Size: int
    StorageClass: str
    Owner: Dict[str, Any]


class S3ResponseTypeDef(TypedDict):
    """Type definition for S3 responses."""

    ResponseMetadata: Dict[str, Any]
    Contents: List[S3ObjectTypeDef]
    Name: str
    Prefix: str
    MaxKeys: int
    IsTruncated: bool


class SQSMessageTypeDef(TypedDict, total=False):
    """Type definition for SQS Message."""

    MessageId: str
    ReceiptHandle: str
    MD5OfBody: str
    Body: str
    Attributes: Dict[str, str]
    MessageAttributes: Dict[str, Dict[str, Any]]


class SQSResponseTypeDef(TypedDict, total=False):
    """Type definition for SQS responses."""

    ResponseMetadata: Dict[str, Any]
    QueueUrl: str
    Messages: List[SQSMessageTypeDef]
    MessageId: str
    MD5OfMessageBody: str
    ReceiptHandle: Optional[str]
