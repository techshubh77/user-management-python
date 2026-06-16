from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "User Management System"
    env: str = "development"
    port: int = 8000
    database_url: str
    jwt_secret: str
    access_token_exp_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


settings = Settings()
