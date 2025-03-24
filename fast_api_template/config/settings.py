"""Application settings and configuration."""

from typing import Any, List, Optional, Union

from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    load_dotenv=True,
    validators=[
        # Server settings
        Validator("server.name", default="FastAPI Template"),
        Validator("server.description", default="A FastAPI template with authentication and cloud services"),
        Validator("server.version", default="0.1.0"),
        Validator("server.docs_url", default="/docs"),
        Validator("server.port", default=8000),
        Validator("server.host", default="0.0.0.0"),
        Validator("server.log_level", default="info"),
        Validator("server.reload", default=False),
        Validator("server.cors_origins", default=["*"]),
        # Database settings
        Validator("database.echo", default=False),
        Validator("database.url", must_exist=True),
        # JWT settings
        Validator("jwt.secret_key", must_exist=True),
        Validator("jwt.algorithm", default="HS256"),
        Validator("jwt.access_token_expire_minutes", default=30),
        # Cloud settings
        Validator("cloud.provider", default="aws"),
        Validator("cloud.aws.access_key_id", when=Validator("cloud.provider", eq="aws")),
        Validator("cloud.aws.secret_access_key", when=Validator("cloud.provider", eq="aws")),
        Validator("cloud.aws.region", when=Validator("cloud.provider", eq="aws")),
        Validator("cloud.gcp.project_id", when=Validator("cloud.provider", eq="gcp")),
        Validator("cloud.gcp.credentials_file", when=Validator("cloud.provider", eq="gcp")),
        Validator("cloud.azure.connection_string", when=Validator("cloud.provider", eq="azure")),
        Validator("cloud.azure.subscription_id", when=Validator("cloud.provider", eq="azure")),
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
