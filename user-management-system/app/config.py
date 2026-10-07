"""
config.py

Reads configuration from the .env file using pydantic-settings.
All environment variables are validated here and accessible via `settings`.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.

    Attributes:
        JWT_SECRET: Secret key used to sign JWT tokens.
        JWT_ALGORITHM: Algorithm used for JWT (default HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES: How long a token is valid.
        DATABASE_URL: SQLAlchemy connection string for the database.
    """

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "sqlite:///./users.db"

    # Tell pydantic-settings to read from a .env file in the current directory.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Single shared instance used throughout the application.
settings = Settings()
