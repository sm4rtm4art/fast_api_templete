"""Application settings and configuration."""

from typing import List, Optional, Union

from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="FAST_API_TEMPLATE",
    settings_files=["config.toml", ".secrets.toml", "default.toml"],
    environments=True,
    load_dotenv=True,
    validators=[
        # Server settings
        Validator("server.name", default="FastAPI Template"),
        Validator("server.description", default="A FastAPI template with authentication and cloud services"),
        Validator("server.version", default="0.1.0"),
        Validator("server.docs_url", default="/docs"),
        Validator("server.port", default=8000),
        Validator("server.host", default="127.0.0.1"),
        Validator("server.log_level", default="info"),
        Validator("server.reload", default=False),
        Validator("server.cors_origins", default=["*"]),
        Validator("server.cors_allow_credentials", default=True),
        # Database settings
        Validator("database.echo", default=False),
        Validator("database.url", required=True),
        # JWT settings
        Validator("jwt.secret_key", required=True),
        Validator("jwt.algorithm", default="HS256"),
        Validator("jwt.access_token_expire_minutes", default=30),
        Validator("jwt.refresh_token_expire_days", default=7),
        # Cloud settings
        Validator("cloud.provider", default="local"),
        Validator("cloud.aws.region", default="us-east-1"),
        Validator("cloud.aws.bucket", default="fast-api-template"),
        Validator("cloud.azure.connection_string", required=False),
        Validator("cloud.azure.container", default="fast-api-template"),
        Validator("cloud.gcp.project_id", required=False),
        Validator("cloud.gcp.bucket", default="fast-api-template"),
        Validator("cloud.local.storage_path", default="local_storage"),
    ],
)


# Type hints for settings
class Settings:
    """Type hints for settings."""

    # Server
    SERVER_NAME: str
    SERVER_DESCRIPTION: str
    SERVER_VERSION: str
    SERVER_DOCS_URL: str
    SERVER_LOG_LEVEL: str
    SERVER_RELOAD: bool
    SERVER_CORS_ORIGINS: Union[str, List[str], None]
    SERVER_PORT: int
    SERVER_HOST: str

    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Cloud
    CLOUD_PROVIDER: str
    CLOUD_REGION: str
    CLOUD_PROJECT_ID: Optional[str]
    CLOUD_TENANT_ID: Optional[str]

    # AWS
    AWS_PROFILE: Optional[str]
    AWS_ROLE_ARN: Optional[str]
    AWS_S3_BUCKET: Optional[str]
    AWS_ELASTICACHE_ENDPOINT: Optional[str]
    AWS_SQS_QUEUE_URL: Optional[str]

    # GCP
    GCP_CREDENTIALS_PATH: Optional[str]
    GCP_STORAGE_BUCKET: Optional[str]
    GCP_PUBSUB_TOPIC: Optional[str]
    GCP_PUBSUB_SUBSCRIPTION: Optional[str]
    GCP_MEMORYSTORE_INSTANCE: Optional[str]

    # Azure
    AZURE_SUBSCRIPTION_ID: Optional[str]
    AZURE_RESOURCE_GROUP: Optional[str]
    AZURE_STORAGE_CONTAINER: Optional[str]
    AZURE_STORAGE_ACCOUNT_NAME: Optional[str]
    AZURE_SERVICEBUS_NAMESPACE: Optional[str]
    AZURE_SERVICEBUS_QUEUE: Optional[str]
    AZURE_CACHE_NAME: Optional[str]
    AZURE_CONNECTION_STRING: Optional[str]


# For type checking
SERVER_NAME: str = settings.server.name
SERVER_DESCRIPTION: str = settings.server.description
SERVER_VERSION: str = settings.server.version
SERVER_DOCS_URL: str = settings.server.docs_url
SERVER_PORT: int = settings.server.port
SERVER_HOST: str = settings.server.host
SERVER_LOG_LEVEL: str = settings.server.log_level
SERVER_RELOAD: bool = settings.server.reload
SERVER_CORS_ORIGINS: Union[str, List[str], None] = settings.server.cors_origins
