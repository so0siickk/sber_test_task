from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    bot_token: str
    admin_ids: list[int]
    llm_api_key: str = "mock_key"
    llm_api_base: str = "mock_base"
    llm_model_name: str = "llama-3.1-8b-instant"
    llm_request_timeout: int = 30
    llm_retries: int = 3
    db_url: str = "sqlite+aiosqlite:///db.sqlite3"


settings = Settings()
