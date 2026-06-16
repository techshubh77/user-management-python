from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "User Management System"
    env: str = "development"
    port: int = 8000
    base_url: str = "http://localhost:8000"
    uploads_dir: str = "uploads"

    database_url: str
    jwt_secret: str
    access_token_exp_minutes: int = 60
    allowed_origins: str

    mailtrap_host: str
    mailtrap_port: int
    mailtrap_user: str
    mailtrap_password: str
    mailtrap_secure: bool = False

    mail_from_name: str = "User Management System"
    mail_from_email: str = "no-reply@usermanagement.com"

    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=False, 
        extra="ignore"
    )


settings = Settings()
