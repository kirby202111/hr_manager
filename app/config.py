from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "sqlite:///./data/hr_system.db"

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    agent_max_iterations: int = 10
    agent_max_history_messages: int = 50
    use_skill_routing: bool = True
    default_user_tag: str = "default"

    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_embedding_model: str = "text-embedding-v3"
    knowledge_base_dir: str = "./data/knowledge_base"
    knowledge_base_chunk_size: int = 500
    knowledge_base_chunk_overlap: int = 100
    knowledge_base_search_top_k: int = 5


settings = Settings()
