from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    mongo_url: str
    db_name: str
    cors_origins: str = "*"
    emergent_llm_key: str = ""
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
