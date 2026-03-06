from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "tokentoast-api"
    ENVIRONMENT: str = "dev" # dev/prod
    DEBUG: bool = True
    SECRET_KEY: str 

    DATABASE_URL: str 
    REDIS_URL: str 

    ACCESS_TOKEN_TTL: int = 30 * 60 # 30 minutes
    REFRESH_TOKEN_TTL: int = 7 * 24 * 60 * 60 # 7 days
    ALGORITHM: str = "HS256"
    BCRYPT_ROUNDS: int = 12

    API_PREFIX: str = "/api"
    API_VERSION: str = "v1"

    FRONTEND_URL: str = "http://localhost:3000"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = ""

    @property
    def API_V1_PREFIX(self) -> str:
        return f"{self.API_PREFIX}/{self.API_VERSION}"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

settings = Settings()