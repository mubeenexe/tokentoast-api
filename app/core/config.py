from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "tokentoast-api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "secret-key"

    DATABASE_URL: str = ""

    API_PREFIX: str = "/api/"
    API_VERSION: str = "v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

settings = Settings()