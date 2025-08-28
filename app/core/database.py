"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Database engine configuration - supports both SQLite and PostgreSQL
connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": settings.DEBUG
}

if settings.DATABASE_URL.startswith('postgresql://') or settings.DATABASE_URL.startswith('postgres://'):
    # PostgreSQL configuration for Render
    connect_args = {"sslmode": "require"}
    engine_kwargs.update({
        "pool_recycle": 300,
        "pool_size": 10,
        "max_overflow": 20,
        "connect_args": connect_args
    })
elif settings.DATABASE_URL.startswith('sqlite://'):
    # SQLite configuration for local development
    connect_args = {"check_same_thread": False}
    engine_kwargs.update({
        "connect_args": connect_args
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

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
