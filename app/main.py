"""
Multi-Armed Bandit Optimization API
Main FastAPI application with SQL integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List
import uvicorn
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Debug environment variables
logger.info("=== ENVIRONMENT DEBUG ===")
logger.info(f"DATABASE_URL exists: {'DATABASE_URL' in os.environ}")
if 'DATABASE_URL' in os.environ:
    db_url = os.environ['DATABASE_URL']
    # Hide password for logging
    if '@' in db_url:
        parts = db_url.split('@')
        safe_url = parts[0].split('://')[0] + '://***@' + '@'.join(parts[1:])
    else:
        safe_url = db_url
    logger.info(f"DATABASE_URL value: {safe_url}")
else:
    logger.warning("DATABASE_URL not found in environment variables")

logger.info(f"All env vars: {list(os.environ.keys())}")
logger.info("=== END ENVIRONMENT DEBUG ===")

from app.core.database import SessionLocal, engine
from .models import Base, Allocation, Experiment
from .schemas import (
    ExperimentCreate, ExperimentResponse,
    MetricDataCreate, MetricDataResponse,
    AllocationResponse
)
from .crud import (
    create_experiment, get_experiment, create_daily_metrics,
    get_experiment_metrics, create_allocation
)
from app.services.bandit import ThompsonSampling
from app.core.config import settings

# Create database tables with retry logic
def create_tables():
    """Create database tables with retry logic"""
    import time
    max_retries = 5
    for attempt in range(max_retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Failed to create tables (attempt {attempt + 1}/{max_retries}): {e}")
                time.sleep(5)
            else:
                logger.error(f"Failed to create tables after {max_retries} attempts: {e}")
                # Don't fail the app startup, let it try to connect later
                pass

create_tables()


app = FastAPI(
    title="Multi-Armed Bandit Optimization API",
    description="API for optimizing A/B test allocation using Thompson Sampling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """API health check"""
    return {"message": "Multi-Armed Bandit Optimization API", "version": "1.0.0"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for Render"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the interactive dashboard"""
    try:
        # Try to read from the root directory first
        dashboard_path = "bandit-dashboard.html"
        if os.path.exists(dashboard_path):
            with open(dashboard_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            # Fallback to app directory
            dashboard_path = os.path.join("app", "dashboard", "index.html")
            if os.path.exists(dashboard_path):
                with open(dashboard_path, "r", encoding="utf-8") as f:
                    content = f.read()
            else:
                # Return a simple message if dashboard not found
                content = """
                <!DOCTYPE html>
                <html>
                <head><title>Dashboard</title></head>
                <body>
                    <h1>Multi-Armed Bandit Dashboard</h1>
                    <p>Dashboard em desenvolvimento. Acesse a <a href="/docs">documentação da API</a>.</p>
                </body>
                </html>
                """
        
        # Replace localhost URLs with current host for production
        content = content.replace("http://localhost:8000", "")
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading dashboard: {str(e)}</h1>")

@app.post("/experiments", response_model=ExperimentResponse)
async def create_new_experiment(
    experiment: ExperimentCreate, 
    db: Session = Depends(get_db)
):
    """Create a new A/B test experiment"""
    return create_experiment(db=db, experiment=experiment)

@app.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment_details(
    experiment_id: int, 
    db: Session = Depends(get_db)
):
    """Get experiment details"""
    experiment = get_experiment(db=db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment

@app.post("/events")
async def submit_events(
    data: dict,
    db: Session = Depends(get_db)
):
    """Submit temporal data for Multi-Armed Bandit experiment"""
    try:
        from datetime import date as date_type
        from app.models import DailyMetric

        experiment_id = data["experiment_id"]
        date_str = data["date"]
        variants = data["variants"]

        # Para cada variante, criar métrica
        for variant in variants:
            # Verificar se já existe
            existing = db.query(DailyMetric).filter(
                DailyMetric.experiment_id == experiment_id,
                DailyMetric.variant_name == variant["variant_name"],
                DailyMetric.date == date_type.fromisoformat(date_str)
            ).first()

            if existing:
                # Atualizar
                existing.impressions = variant["impressions"]
                existing.clicks = variant["clicks"]
            else:
                # Criar novo
                metric = DailyMetric(
                    experiment_id=experiment_id,
                    variant_name=variant["variant_name"],
                    date=date_type.fromisoformat(date_str),
                    impressions=variant["impressions"],
                    clicks=variant["clicks"]
                )
                db.add(metric)

        db.commit()
        return {"status": "success", "variants_processed": len(variants)}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from sqlalchemy import func
from app.models import DailyMetric

@app.get("/allocation", response_model=AllocationResponse)
async def get_allocation(
    experiment_id: int,
    window_days: int = 14,
    db: Session = Depends(get_db)
):
    """Get optimal traffic allocation using Thompson Sampling"""
    # 1. Verifica se o experimento existe
    experiment = db.query(Experiment).filter_by(id=experiment_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail="Experimento não encontrado"
        )

    # 2. Obtém dados do experimento
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=window_days)

    metrics = db.query(
        DailyMetric.variant_name,
        func.sum(DailyMetric.impressions).label('impressions'),
        func.sum(DailyMetric.clicks).label('clicks')
    ).filter(
        DailyMetric.experiment_id == experiment_id,
        DailyMetric.date >= start_date,
        DailyMetric.date <= end_date
    ).group_by(DailyMetric.variant_name
    ).having(func.sum(DailyMetric.impressions) > 0).all()

    # 3. Diagnóstico para dados insuficientes
    if not metrics or len(metrics) < 2:
        all_data = db.query(func.count(func.distinct(DailyMetric.variant_name)).label("variants")).filter(
            DailyMetric.experiment_id == experiment_id
        ).first()
        if all_data and all_data.variants < 2:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Insufficient variants",
                    "details": "É necessário pelo menos 2 variantes para calcular alocação",
                    "found_variants": all_data.variants
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "No data in time window",
                    "details": f"Nenhum dado encontrado para os últimos {window_days} dias",
                    "experiment_id": experiment_id,
                    "window_days": window_days
                }
            )

    # 4. Prepara dados para Thompson Sampling
    variant_data = []
    for m in metrics:
        variant_data.append({
            "name": m.variant_name,
            "impressions": m.impressions or 0,
            "clicks": m.clicks or 0
        })

    # 5. Calcula alocação
    bandit = ThompsonSampling()
    allocations = bandit.calculate_allocation(variant_data)

    # 6. Salva a alocação no histórico
    from app.models import Allocation
    target_date = datetime.now(timezone.utc).date()
    db_allocation = Allocation(
        experiment_id=experiment_id,
        target_date=target_date,
        algorithm="thompson_sampling",
        allocations=allocations,
        window_days=window_days,
        total_impressions=sum(v["impressions"] for v in variant_data),
        total_clicks=sum(v["clicks"] for v in variant_data)
    )
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)

    # 7. Busca histórico recente
    history = db.query(Allocation).filter(
        Allocation.experiment_id == experiment_id
    ).order_by(Allocation.target_date.desc()).limit(10).all()
    history_data = [
        {
            "date": alloc.target_date.isoformat(),
            "allocations": alloc.allocations,
            "algorithm": alloc.algorithm,
            "window_days": alloc.window_days,
            "total_impressions": alloc.total_impressions,
            "total_clicks": alloc.total_clicks
        }
        for alloc in history
    ]

    # 8. Retorna resposta tipo dashboard
    return {
        "allocations": allocations,
        "algorithm": "thompson_sampling",
        "parameters": {
            "min_explore_rate": bandit.min_explore_rate,
            "control_floor": bandit.control_floor,
            "max_daily_shift": bandit.max_daily_shift
        },
        "experiment_id": experiment_id,
        "window_days": window_days,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_impressions": sum(v["impressions"] for v in variant_data),
            "total_clicks": sum(v["clicks"] for v in variant_data),
            "variants": variant_data
        },
        "history": history_data
    }

from typing import Optional

from typing import Optional
from sqlalchemy import text

@app.get("/experiments/{experiment_id}/history")
async def get_allocation_history(
    experiment_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get allocation history for an experiment, optionally filtered by date range"""
    experiment = get_experiment(db=db, experiment_id=experiment_id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")

    query = db.query(Allocation).filter(Allocation.experiment_id == experiment_id)
    if start_date:
        from datetime import date
        query = query.filter(Allocation.target_date >= date.fromisoformat(start_date))
    if end_date:
        from datetime import date
        query = query.filter(Allocation.target_date <= date.fromisoformat(end_date))
    allocations = query.order_by(Allocation.target_date.desc()).limit(30).all()

    return {
        "experiment_id": experiment_id,
        "history": [
            {
                "date": alloc.target_date.isoformat(),
                "algorithm": alloc.algorithm,
                "allocations": alloc.allocations,
                "total_impressions": alloc.total_impressions,
                "total_clicks": alloc.total_clicks
            }
            for alloc in allocations
        ]
    }

@app.post("/migrate_database")
async def migrate_database(db: Session = Depends(get_db)):
    """Manually run database migrations"""
    try:
        # Read and execute the init.sql file
        import os
        sql_file_path = os.path.join("scripts", "init.sql")
        
        if os.path.exists(sql_file_path):
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Execute the SQL commands
            db.execute(text(sql_content))
            db.commit()
            
            return {"message": "✅ Database migrated successfully!", "status": "success"}
        else:
            # Fallback: create tables using SQLAlchemy
            Base.metadata.create_all(bind=engine)
            db.commit()
            return {"message": "✅ Database tables created using SQLAlchemy!", "status": "success"}
            
    except Exception as e:
        db.rollback()
        logger.error(f"Database migration failed: {e}")
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

@app.post("/reset_data")
async def reset_data(db: Session = Depends(get_db)):
    """Resets all data in the database"""
    try:
        db.execute(text("TRUNCATE TABLE daily_metrics, allocations, experiments RESTART IDENTITY CASCADE;"))
        db.commit()
        return {"message": "Dados limpos com sucesso!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao limpar dados: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
