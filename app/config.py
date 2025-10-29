"""Application configuration management."""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Fake Review Detection System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Database
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ML Models
    MODEL_PATH: str = "data/models"
    MODEL_VERSION: str = "v1.0"
    PREDICTION_THRESHOLD: float = 0.5
    ENSEMBLE_WEIGHTS: str = "0.4,0.35,0.25"
    
    # Scraping
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    SCRAPER_HEADLESS: bool = True
    SCRAPER_TIMEOUT: int = 30
    SCRAPER_RATE_LIMIT: int = 2
    SCRAPER_MAX_RETRIES: int = 3
    
    # Amazon
    AMAZON_BASE_URL: str = "https://www.amazon.com"
    AMAZON_API_KEY: str = ""
    
    # Flipkart
    FLIPKART_BASE_URL: str = "https://www.flipkart.com"
    FLIPKART_API_KEY: str = ""
    
    # NLP
    NLP_MODEL: str = "bert-base-uncased"
    NLP_MAX_LENGTH: int = 512
    NLP_BATCH_SIZE: int = 32
    NLTK_DATA_PATH: str = "./nltk_data"
    
    # Flagging
    FAKE_PROBABILITY_THRESHOLD: float = 0.7
    SUSPICIOUS_REVIEW_BURST: int = 5
    TRUST_SCORE_MIN: float = 0.3
    IP_CLUSTER_THRESHOLD: int = 10
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    NOTIFICATION_FROM: str = ""
    ADMIN_EMAIL: str = ""
    
    # Authentication
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "logs/app.log"
    
    @property
    def ensemble_weights_list(self) -> List[float]:
        """Parse ensemble weights from string."""
        return [float(w) for w in self.ENSEMBLE_WEIGHTS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
