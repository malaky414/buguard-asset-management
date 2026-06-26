from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str = ""
    POSTGRES_USER: str = "buguard"
    POSTGRES_PASSWORD: str = "buguard_pass"
    POSTGRES_DB: str = "asset_db"
    LLM_PROVIDER: str = "openai"
    API_SECRET_KEY: str = "changeme"

class Config:
    env_file = ".env"
    extra = "ignore"

settings = Settings()
