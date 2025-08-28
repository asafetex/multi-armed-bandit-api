"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create database engine with Render-specific optimizations
def create_database_engine():
    """Create database engine with proper configuration for Render"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Log the database URL for debugging
    db_url = settings.DATABASE_URL
    if '@' in db_url:
        parts = db_url.split('@')
        safe_url = parts[0].split('://')[0] + '://***@' + '@'.join(parts[1:])
    else:
        safe_url = db_url
    logger.info(f"Creating engine with URL: {safe_url}")
    
    # Configure connection arguments for PostgreSQL on Render
    connect_args = {
        "connect_timeout": 60,
        "application_name": "multi-armed-bandit-api"
    }
    
    # Add SSL configuration for Render PostgreSQL
    if "render.com" in db_url or "onrender.com" in db_url:
        connect_args["sslmode"] = "require"
        logger.info("SSL mode enabled for Render PostgreSQL")
    
    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10,
        echo=settings.DEBUG,
        connect_args=connect_args
    )

engine = create_database_engine()

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
