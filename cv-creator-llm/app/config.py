"""
Configuration settings for CV Creator LLM application
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "CV Creator using LLMs"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Models (will be set via UI selection)
    TEXT_MODEL: str = ""  # Legacy - for backwards compatibility
    VISION_MODEL: str = ""  # For vision tasks
    PARSING_MODEL: str = ""  # For resume parsing/extraction (selected via UI)
    GENERATION_MODEL: str = ""  # For resume generation/tailoring (selected via UI)

    # Model Parameters
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    TOP_P: float = 0.9

    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".docx", ".doc", ".txt"}
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"

    # Resume Processing
    EXTRACT_TIMEOUT: int = 30  # seconds
    GENERATION_TIMEOUT: int = 60  # seconds

    # ATS Optimization
    MIN_KEYWORD_MATCH_SCORE: float = 0.6
    ATS_COMPLIANCE_THRESHOLD: float = 0.75

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs("samples/resumes", exist_ok=True)
os.makedirs("samples/job_descriptions", exist_ok=True)
os.makedirs("samples/outputs", exist_ok=True)
