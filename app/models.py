"""
SQLAlchemy models for Multi-Armed Bandit API
Efficient database schema for experiment tracking
"""

from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, Float, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
import os
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Experiment(Base):
    """Experiment model - represents an A/B test experiment"""
    __tablename__ = "experiments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    daily_metrics = relationship("DailyMetric", back_populates="experiment")
    allocations = relationship("Allocation", back_populates="experiment")

class DailyMetric(Base):
    """Daily metrics model - stores performance data for each variant per day"""
    __tablename__ = "daily_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    variant_name = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="daily_metrics")
    
    # Composite indexes for efficient queries
    __table_args__ = (
        Index('idx_experiment_variant_date', 'experiment_id', 'variant_name', 'date'),
        Index('idx_experiment_date', 'experiment_id', 'date'),
    )

class Allocation(Base):
    """Allocation model - stores calculated traffic allocations"""
    __tablename__ = "allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    target_date = Column(Date, nullable=False)
    algorithm = Column(String(50), default="thompson_sampling")
    # Use JSONB for PostgreSQL (Render) or JSON for SQLite (local development)
    allocations = Column(
        MutableDict.as_mutable(JSONB) if 'postgresql' in os.getenv('DATABASE_URL', '') or 'postgres' in os.getenv('DATABASE_URL', '') 
        else JSON, 
        nullable=True
    )  # {"variant_name": percentage}
    window_days = Column(Integer, default=14)
    total_impressions = Column(Integer, default=0)
    total_clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="allocations")
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_experiment_target_date', 'experiment_id', 'target_date'),
    )
