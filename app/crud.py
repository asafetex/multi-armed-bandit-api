"""
CRUD operations with optimized SQL queries
"""

from sqlalchemy.orm import Session
from sqlalchemy import text, and_
from typing import List, Optional
from datetime import date, timedelta

from app.models import Experiment, DailyMetric, Allocation
from app.schemas import ExperimentCreate, MetricDataCreate

def create_experiment(db: Session, experiment: ExperimentCreate) -> Experiment:
    """Create a new experiment"""
    db_experiment = Experiment(
        name=experiment.name,
        description=experiment.description
    )
    db.add(db_experiment)
    db.commit()
    db.refresh(db_experiment)
    return db_experiment

def get_experiment(db: Session, experiment_id: int) -> Optional[Experiment]:
    """Get experiment by ID"""
    return db.query(Experiment).filter(Experiment.id == experiment_id).first()

def create_daily_metrics(
    db: Session, 
    experiment_id: int, 
    data: MetricDataCreate
) -> List[DailyMetric]:
    """Create or update daily metrics for experiment variants"""
    metrics = []
    
    for variant_data in data.variants:
        # Calculate CTR
        ctr = variant_data.clicks / variant_data.impressions if variant_data.impressions > 0 else 0
        
        # Check if metric already exists
        existing_metric = db.query(DailyMetric).filter(
            and_(
                DailyMetric.experiment_id == experiment_id,
                DailyMetric.variant_name == variant_data.name,
                DailyMetric.date == data.date
            )
        ).first()
        
        if existing_metric:
            # Update existing metric
            existing_metric.impressions = variant_data.impressions
            existing_metric.clicks = variant_data.clicks
            existing_metric.conversions = variant_data.conversions
            existing_metric.ctr = ctr
            metrics.append(existing_metric)
        else:
            # Create new metric
            db_metric = DailyMetric(
                experiment_id=experiment_id,
                variant_name=variant_data.name,
                date=data.date,
                impressions=variant_data.impressions,
                clicks=variant_data.clicks,
                conversions=variant_data.conversions,
                ctr=ctr
            )
            db.add(db_metric)
            metrics.append(db_metric)
    
    db.commit()
    
    for metric in metrics:
        db.refresh(metric)
    
    return metrics

def get_experiment_metrics(
    db: Session, 
    experiment_id: int, 
    window_days: int = 14
) -> List:
    """Get aggregated metrics for experiment using optimized SQL"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=window_days)
    
    # Optimized SQL query with aggregation
    query = text("""
        SELECT 
            variant_name,
            SUM(impressions) as total_impressions,
            SUM(clicks) as total_clicks,
            SUM(conversions) as total_conversions,
            AVG(ctr) as avg_ctr,
            COUNT(*) as days_active
        FROM daily_metrics 
        WHERE experiment_id = :experiment_id 
        AND date >= :start_date 
        AND date <= :end_date
        GROUP BY variant_name
        ORDER BY total_clicks DESC
    """)
    
    result = db.execute(
        query, 
        {
            "experiment_id": experiment_id,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    
    return result.fetchall()

def create_allocation(
    db: Session,
    experiment_id: int,
    target_date: date,
    allocations: dict,
    algorithm: str = "thompson_sampling"
) -> Allocation:
    """Store calculated allocation in database"""
    
    db_allocation = Allocation(
        experiment_id=experiment_id,
        target_date=target_date,
        algorithm=algorithm,
        allocations=allocations
    )
    
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    
    return db_allocation

def get_recent_allocation(
    db: Session,
    experiment_id: int
) -> Optional[Allocation]:
    """Get the most recent allocation for an experiment"""
    return db.query(Allocation).filter(
        Allocation.experiment_id == experiment_id
    ).order_by(Allocation.target_date.desc()).first()
