"""
Configuration settings for the Multi-Armed Bandit API
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings:
    """Application configuration"""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://bandit_user:bandit_pass@localhost:5432/bandit_db"
    )
    
    def __init__(self):
        # Convert postgres:// to postgresql:// if needed (Render compatibility)
        if self.DATABASE_URL.startswith('postgres://'):
            self.DATABASE_URL = self.DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        
        # Log database URL for debugging (hide password)
        db_url_safe = self.DATABASE_URL.replace(self.DATABASE_URL.split('@')[0].split('://')[-1], '***') if '@' in self.DATABASE_URL else self.DATABASE_URL
        logger.info(f"Database URL configured: {db_url_safe}")
        logger.info(f"Environment: {self.ENVIRONMENT}")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    APP_NAME: str = "Multi-Armed Bandit API"
    VERSION: str = "1.0.0"
    
    # Algorithm defaults
    DEFAULT_WINDOW_DAYS: int = int(os.getenv("DEFAULT_WINDOW_DAYS", "14"))
    MIN_IMPRESSIONS_FOR_OPTIMIZATION: int = int(os.getenv("MIN_IMPRESSIONS_FOR_OPTIMIZATION", "1000"))
    
    # Thompson Sampling parameters
    ALPHA_PRIOR: float = float(os.getenv("ALPHA_PRIOR", "1.0"))
    BETA_PRIOR: float = float(os.getenv("BETA_PRIOR", "1.0"))
    MIN_EXPLORE_RATE: float = float(os.getenv("MIN_EXPLORE_RATE", "0.05"))
    CONTROL_FLOOR: float = float(os.getenv("CONTROL_FLOOR", "0.1"))
    MAX_DAILY_SHIFT: float = float(os.getenv("MAX_DAILY_SHIFT", "0.2"))

settings = Settings()
