from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "MY_NOTE_"}

    port: int = 8800
    data_dir: str = "/data"
    qdrant_url: str = "http://qdrant:6333"
    chunk_size: int = 512
    chunk_overlap: int = 50
    embedding_model: str = "voyage-3"
    observe_model: str = "claude-sonnet-4-6"
    think_model: str = "claude-opus-4-6"
    think_budget: int = 6000


settings = Settings()
