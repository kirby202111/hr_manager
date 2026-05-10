from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./hr_system.db"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    agent_max_iterations: int = 10
    agent_max_history_messages: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
