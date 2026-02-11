from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    mongo_url: str = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name: str = os.environ.get('DB_NAME', 'real_estate_platform')
    cors_origins: str = os.environ.get('CORS_ORIGINS', '*')
    emergent_llm_key: str = os.environ.get('EMERGENT_LLM_KEY', '')
    jwt_secret: str = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
