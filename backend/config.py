from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # These are default values that will be overridden by environment variables
    # BASE_URL: str
    MAX_FILES: int = 5  # Reasonable default
    MAX_FILE_SIZE: int = 20 * 1024 * 1024  # 20MB default
    ALLOWED_TYPES: List[str] = ["pdf", "pptx", "docx", "txt"]
    DOWNLOAD_EXPIRY: int = 60*10  # 10 minutes default
    
    # Required settings (no defaults - must be in environment)
    COHERE_API_KEY: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
