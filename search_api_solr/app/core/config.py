from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SOLR_BASE_URL: str = "http://localhost:8983/solr"
    SOLR_CORE_NAME: str = "my_core"

    class Config:
        env_file = ".env"

settings = Settings()
