"""Application settings and configuration using Pydantic Settings."""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Define nested model for DatabaseSettings
class DatabaseSettings(BaseSettings):
    """Database configuration."""

    url: str = Field(...)
    echo: bool = False
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_DATABASE_", env_file=".env", extra="ignore")


# Define nested model for JWTSettings
class JWTSettings(BaseSettings):
    """JWT configuration."""

    secret_key: str = Field(...)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_JWT_", env_file=".env", extra="ignore")


# Define nested model for DemoUserSettings
class DemoUserSettings(BaseSettings):
    """Demo User configuration."""

    password_hash: str = Field(...)
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_DEMO_USER_", env_file=".env", extra="ignore")


# Define nested models for Cloud Settings
class CloudAWSSettings(BaseSettings):
    """AWS specific settings."""

    region: str = "us-east-1"
    bucket: str = "fast-api-template"
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_CLOUD_AWS_", env_file=".env", extra="ignore")


class CloudAzureSettings(BaseSettings):
    """Azure specific settings."""

    connection_string: Optional[str] = None
    container: str = "fast-api-template"
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_CLOUD_AZURE_", env_file=".env", extra="ignore")


class CloudGCPSettings(BaseSettings):
    """GCP specific settings."""

    project_id: Optional[str] = None
    bucket: str = "fast-api-template"
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_CLOUD_GCP_", env_file=".env", extra="ignore")


class CloudLocalSettings(BaseSettings):
    """Local storage settings."""

    storage_path: str = "local_storage"
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_CLOUD_LOCAL_", env_file=".env", extra="ignore")


class CloudSettings(BaseSettings):
    """Cloud configuration."""

    provider: str = "local"
    aws: CloudAWSSettings = Field(default_factory=CloudAWSSettings)
    azure: CloudAzureSettings = Field(default_factory=CloudAzureSettings)
    gcp: CloudGCPSettings = Field(default_factory=CloudGCPSettings)
    local: CloudLocalSettings = Field(default_factory=CloudLocalSettings)
    model_config = SettingsConfigDict(env_prefix="FAST_API_TEMPLATE_CLOUD_", env_file=".env", extra="ignore")


# Main Settings Class inheriting from BaseSettings
class Settings(BaseSettings):
    """Main application settings."""

    # Server settings (keep fields)
    server_name: str = Field("FastAPI Template", alias="FAST_API_TEMPLATE_SERVER_NAME")
    server_description: str = Field(
        "A FastAPI template with authentication and cloud services", alias="FAST_API_TEMPLATE_SERVER_DESCRIPTION"
    )
    server_version: str = Field("0.1.0", alias="FAST_API_TEMPLATE_SERVER_VERSION")
    server_docs_url: str = Field("/docs", alias="FAST_API_TEMPLATE_SERVER_DOCS_URL")
    server_port: int = Field(8000, alias="FAST_API_TEMPLATE_SERVER_PORT")
    server_host: str = Field("127.0.0.1", alias="FAST_API_TEMPLATE_SERVER_HOST")
    server_log_level: str = Field("info", alias="FAST_API_TEMPLATE_SERVER_LOG_LEVEL")
    server_reload: bool = Field(False, alias="FAST_API_TEMPLATE_SERVER_RELOAD")
    server_cors_origins: List[str] = Field(["*"], alias="FAST_API_TEMPLATE_SERVER_CORS_ORIGINS")
    server_cors_allow_credentials: bool = Field(True, alias="FAST_API_TEMPLATE_SERVER_CORS_ALLOW_CREDENTIALS")
    env: str = Field("DEVELOPMENT", alias="FAST_API_TEMPLATE_ENV")

    # Nested settings - Use default_factory and add ignores
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)  # type: ignore[arg-type]
    jwt: JWTSettings = Field(default_factory=JWTSettings)  # type: ignore[arg-type]
    demo_user: DemoUserSettings = Field(default_factory=DemoUserSettings)  # type: ignore[arg-type]
    cloud: CloudSettings = Field(default_factory=CloudSettings)

    model_config = SettingsConfigDict(
        env_prefix="FAST_API_TEMPLATE_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


# Instantiate the settings - Add ignore
settings = Settings()  # type: ignore[call-arg]

# Remove the separate instantiations
# server_settings = ...
# db_settings = ...
# etc.

# Optional: Re-export specific values if needed
# DATABASE_URL: str = settings.database.url
# DATABASE_ECHO: bool = settings.database.echo
# JWT_SECRET_KEY: str = settings.jwt.secret_key
