from pydantic import Field
from pydantic_settings import BaseSettings


class ExtractorConfigs(BaseSettings):
    """The configuration settings for the extractor application"""

    HOST: str = Field(default="")
    DATABASE: str = Field(default="")
    USERNAME_MYSQL: str = Field(default="")
    PASSWORD: str = Field(default="")
    AZURE_BLOB_STORAGE_ACCOUNT: str = Field(default="")
    AZURE_BLOB_STORAGE_CONTAINER: str = Field(default="")
    AZURE_BLOB_STORAGE_KEY: str = Field(default="")



    AZ_ST_ACC_NAME: str = Field(default="")
    AZ_ST_ACC_KEY: str = Field(default="")
    AZ_ST_CONTAINER_NAME: str = Field(default="")
    AZ_ST_DATASOURCE_CONTAINER_NAME: str = Field(default="")

    UPLOAD_DIR: str = Field(default="")
    PREDICTIONS_DIR: str = Field(default="")
    BASE_URL: str = Field(default="")
    BASE_UI_URL: str = Field(default="")

    DB_TYPE: str = Field(default="")
    DATABASE_FILE: str = Field(default="")

    SECRET_KEY: str = Field(default="")
    SALT: str = Field(default="")

    SMTP_SERVER: str = Field(default="")
    SMTP_port: str = Field(default="")
    SENDER_USERNAME: str = Field(default="")
    SENDER_PASSWORD: str = Field(default="")

    USERNAME_MYSQL: str = Field(default="")
    PASSWORD: str = Field(default="")
    HOST: str = Field(default="")

    STRIPE_WEBHOOK_KEY: str = Field(default="")
    STRIPE_API_KEY: str = Field(default="")

    BEES_PREMIUM_SUBSCRIPTION: str = Field(default="")
    BEES_RESEARCH_SUBSCRIPTION: str = Field(default="")