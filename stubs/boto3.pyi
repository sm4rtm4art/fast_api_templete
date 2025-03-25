"""Type stubs for boto3."""

from typing import Any, Literal, Optional, Union, overload

from mypy_boto3_lambda.client import LambdaClient
from mypy_boto3_rds.client import RDSClient
from mypy_boto3_s3.client import S3Client
from mypy_boto3_sqs.client import SQSClient

class Config:
    """Boto3 config class."""

@overload
def client(
    service_name: Literal["s3"],
    region_name: Optional[str] = None,
    api_version: Optional[str] = None,
    use_ssl: Optional[bool] = None,
    verify: Optional[Union[bool, str]] = None,
    endpoint_url: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    config: Optional[Config] = None,
    aws_account_id: Optional[str] = None,
) -> S3Client: ...
@overload
def client(
    service_name: Literal["sqs"],
    region_name: Optional[str] = None,
    api_version: Optional[str] = None,
    use_ssl: Optional[bool] = None,
    verify: Optional[Union[bool, str]] = None,
    endpoint_url: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    config: Optional[Config] = None,
    aws_account_id: Optional[str] = None,
) -> SQSClient: ...
@overload
def client(
    service_name: Literal["lambda"],
    region_name: Optional[str] = None,
    api_version: Optional[str] = None,
    use_ssl: Optional[bool] = None,
    verify: Optional[Union[bool, str]] = None,
    endpoint_url: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    config: Optional[Config] = None,
    aws_account_id: Optional[str] = None,
) -> LambdaClient: ...
@overload
def client(
    service_name: Literal["rds"],
    region_name: Optional[str] = None,
    api_version: Optional[str] = None,
    use_ssl: Optional[bool] = None,
    verify: Optional[Union[bool, str]] = None,
    endpoint_url: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    config: Optional[Config] = None,
    aws_account_id: Optional[str] = None,
) -> RDSClient: ...
@overload
def client(
    service_name: str,
    region_name: Optional[str] = None,
    api_version: Optional[str] = None,
    use_ssl: Optional[bool] = None,
    verify: Optional[Union[bool, str]] = None,
    endpoint_url: Optional[str] = None,
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    config: Optional[Config] = None,
    aws_account_id: Optional[str] = None,
) -> Any: ...
