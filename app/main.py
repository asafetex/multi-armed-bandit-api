"""
Multi-Armed Bandit Optimization API
Main FastAPI application with SQL integration
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text, Integer
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
from .models import Base, Allocation, Experiment, DailyMetric
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
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.fetchone()[0]
        db_status = "healthy" if test_value == 1 else "unhealthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if "healthy" in db_status else "unhealthy",
        "database": db_status,
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "database_url_configured": "DATABASE_URL" in os.environ
    }

# Removed /db-test endpoint - security risk, exposes sensitive database information

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
        content = content.replace("window.location.origin", f"'{os.getenv('RENDER_EXTERNAL_URL', 'http://localhost:8080')}'")
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading dashboard: {str(e)}</h1>")

# Removed /bandit-dashboard.html endpoint - duplicate of /dashboard

@app.post("/experiments/", response_model=ExperimentResponse)
async def create_new_experiment(
    experiment: ExperimentCreate, 
    db: Session = Depends(get_db)
):
    """Create a new A/B test experiment"""
    return create_experiment(db=db, experiment=experiment)

@app.get("/experiments/", response_model=List[ExperimentResponse])
async def list_experiments(db: Session = Depends(get_db)):
    """List all experiments with their metrics"""
    experiments = db.query(Experiment).all()
    
    # Add metrics to each experiment for dashboard display
    for exp in experiments:
        metrics = db.query(DailyMetric).filter(
            DailyMetric.experiment_id == exp.id
        ).all()
        
        # Add metrics as a property for the response
        exp.metrics = [
            {
                "date": m.date.isoformat() if m.date else None,
                "variant_name": m.variant_name,
                "impressions": m.impressions,
                "clicks": m.clicks, 
                "conversions": m.conversions,
                "ctr": m.ctr
            }
            for m in metrics
        ]
    
    return experiments

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
        
        # Handle both formats: with variants array or direct variant data
        if "variants" in data:
            variants = data["variants"]
        else:
            # Single variant format from dashboard
            variants = [{
                "variant_name": data["variant_name"],
                "impressions": data["impressions"],
                "clicks": data["clicks"],
                "conversions": data.get("conversions", 0)
            }]

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
                existing.conversions = variant.get("conversions", 0)
            else:
                # Criar novo
                metric = DailyMetric(
                    experiment_id=experiment_id,
                    variant_name=variant["variant_name"],
                    date=date_type.fromisoformat(date_str),
                    impressions=variant["impressions"],
                    clicks=variant["clicks"],
                    conversions=variant.get("conversions", 0)
                )
                db.add(metric)

        db.commit()
        return {"status": "success", "variants_processed": len(variants)}

    except Exception as e:
        db.rollback()
        logger.error(f"Error in submit_events: {str(e)}")
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

    logger.info(f"Querying metrics for experiment {experiment_id}, date range: {start_date} to {end_date}")

    try:
        # Cast to avoid PostgreSQL type issues
        metrics = db.query(
            DailyMetric.variant_name,
            func.sum(func.cast(DailyMetric.impressions, Integer)).label('impressions'),
            func.sum(func.cast(DailyMetric.clicks, Integer)).label('clicks'),
            func.sum(func.cast(DailyMetric.conversions, Integer)).label('conversions')
        ).filter(
            DailyMetric.experiment_id == experiment_id,
            DailyMetric.date >= start_date,
            DailyMetric.date <= end_date
        ).group_by(DailyMetric.variant_name
        ).having(func.sum(func.cast(DailyMetric.impressions, Integer)) > 0).all()
        
        logger.info(f"Found {len(metrics)} variant metrics for experiment {experiment_id}")
        for m in metrics:
            logger.info(f"  {m.variant_name}: {m.impressions} impressions, {m.clicks} clicks, {m.conversions} conversions")
        
    except Exception as e:
        logger.error(f"Error querying metrics for experiment {experiment_id}: {str(e)}")
        # Try simpler query as fallback
        try:
            logger.info("Trying fallback query without casting...")
            metrics = db.query(
                DailyMetric.variant_name,
                func.sum(DailyMetric.impressions).label('impressions'),
                func.sum(DailyMetric.clicks).label('clicks'),
                func.sum(DailyMetric.conversions).label('conversions')
            ).filter(
                DailyMetric.experiment_id == experiment_id,
                DailyMetric.date >= start_date,
                DailyMetric.date <= end_date
            ).group_by(DailyMetric.variant_name).all()
            
            # Filter out zero impressions in Python instead of SQL
            metrics = [m for m in metrics if (m.impressions or 0) > 0]
            logger.info(f"Fallback query successful: {len(metrics)} variants found")
            
        except Exception as e2:
            logger.error(f"Fallback query also failed: {str(e2)}")
            raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")

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
            "clicks": m.clicks or 0,
            "conversions": m.conversions or 0
        })

    # 5. Calcula alocação
    bandit = ThompsonSampling()
    allocations = bandit.calculate_allocation(variant_data)

    # 6. Salva a alocação no histórico
    from app.models import Allocation
    target_date = datetime.now(timezone.utc).date()
    
    # Convert allocations to ensure JSON compatibility across databases
    allocations_json = dict(allocations) if allocations else {}
    
    try:
        db_allocation = Allocation(
            experiment_id=experiment_id,
            target_date=target_date,
            algorithm="thompson_sampling",
            allocations=allocations_json,
            window_days=window_days,
            total_impressions=sum(v["impressions"] for v in variant_data),
            total_clicks=sum(v["clicks"] for v in variant_data)
        )
        db.add(db_allocation)
        db.commit()
        db.refresh(db_allocation)
        logger.info(f"Allocation saved successfully for experiment {experiment_id}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save allocation for experiment {experiment_id}: {str(e)}")
        # Continue without saving allocation to avoid breaking the endpoint
        logger.warning("Continuing without saving allocation to database")

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

# Removed /migrate_database endpoint - security risk, allows unprotected database migration

@app.get("/download-template")
async def download_template():
    """Download CSV template for bulk data upload"""
    template_path = "modelo_dados_bandit.csv"
    if os.path.exists(template_path):
        return FileResponse(
            path=template_path,
            filename="modelo_dados_bandit.csv",
            media_type="text/csv"
        )
    else:
        raise HTTPException(status_code=404, detail="Template file not found")

@app.post("/upload-data")
async def upload_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload bulk data from CSV file"""
    import csv
    import io
    from datetime import date as date_type
    from app.models import DailyMetric
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Validate headers
        expected_headers = {'experiment_id', 'date', 'variant_name', 'impressions', 'clicks', 'conversions'}
        if not expected_headers.issubset(set(csv_reader.fieldnames)):
            raise HTTPException(
                status_code=400, 
                detail=f"CSV must contain headers: {', '.join(expected_headers)}"
            )
        
        processed_rows = 0
        errors = []
        experiment_ids_used = set()
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is headers
            try:
                # Parse and validate data
                experiment_id = int(row['experiment_id'])
                date_str = row['date']
                variant_name = row['variant_name'].strip()
                impressions = int(row['impressions'])
                clicks = int(row['clicks'])
                conversions = int(row.get('conversions', 0))
                
                # Validate business rules
                if clicks > impressions:
                    errors.append(f"Row {row_num}: clicks ({clicks}) cannot be greater than impressions ({impressions})")
                    continue
                
                if conversions > clicks:
                    errors.append(f"Row {row_num}: conversions ({conversions}) cannot be greater than clicks ({clicks})")
                    continue
                
                # Check if experiment exists
                experiment = db.query(Experiment).filter_by(id=experiment_id).first()
                if not experiment:
                    errors.append(f"Row {row_num}: experiment_id {experiment_id} not found")
                    continue
                
                # Parse date
                try:
                    parsed_date = date_type.fromisoformat(date_str)
                except ValueError:
                    errors.append(f"Row {row_num}: invalid date format '{date_str}'. Use YYYY-MM-DD")
                    continue
                
                # Check if record already exists
                existing = db.query(DailyMetric).filter(
                    DailyMetric.experiment_id == experiment_id,
                    DailyMetric.variant_name == variant_name,
                    DailyMetric.date == parsed_date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.impressions = impressions
                    existing.clicks = clicks
                    existing.conversions = conversions
                else:
                    # Create new record
                    metric = DailyMetric(
                        experiment_id=experiment_id,
                        variant_name=variant_name,
                        date=parsed_date,
                        impressions=impressions,
                        clicks=clicks,
                        conversions=conversions
                    )
                    db.add(metric)
                
                # Track experiment ID used
                experiment_ids_used.add(experiment_id)
                processed_rows += 1
                
            except ValueError as e:
                errors.append(f"Row {row_num}: invalid data format - {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        # Commit if we have processed rows
        if processed_rows > 0:
            db.commit()
        
        return {
            "status": "success" if processed_rows > 0 else "error",
            "processed_rows": processed_rows,
            "total_rows": csv_reader.line_num - 1,  # Subtract header row
            "errors": errors[:10],  # Limit errors to first 10
            "total_errors": len(errors),
            "experiment_ids": sorted(list(experiment_ids_used))
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/reset_data")
async def reset_data(db: Session = Depends(get_db)):
    """Resets all data in the database"""
    try:
        # Get actual database URL from engine
        from app.core.database import engine
        db_url = str(engine.url)
        
        # Detect database type from actual connection
        is_sqlite = db_url.startswith('sqlite')
        is_postgresql = 'postgresql' in db_url or 'postgres' in db_url
        
        logger.info(f"Database type detection: URL={db_url[:20]}..., SQLite={is_sqlite}, PostgreSQL={is_postgresql}")
        
        if is_sqlite:
            # SQLite doesn't support TRUNCATE, use DELETE
            db.execute(text("DELETE FROM daily_metrics;"))
            db.execute(text("DELETE FROM allocations;"))
            db.execute(text("DELETE FROM experiments;"))
            # Reset auto-increment counters for SQLite
            db.execute(text("DELETE FROM sqlite_sequence WHERE name IN ('daily_metrics', 'allocations', 'experiments');"))
        elif is_postgresql:
            # PostgreSQL - use TRUNCATE with CASCADE to handle foreign key constraints
            db.execute(text("TRUNCATE TABLE daily_metrics RESTART IDENTITY CASCADE;"))
            db.execute(text("TRUNCATE TABLE allocations RESTART IDENTITY CASCADE;"))
            db.execute(text("TRUNCATE TABLE experiments RESTART IDENTITY CASCADE;"))
        else:
            # Fallback for other databases - use DELETE
            db.execute(text("DELETE FROM daily_metrics;"))
            db.execute(text("DELETE FROM allocations;"))
            db.execute(text("DELETE FROM experiments;"))
        
        db.commit()
        logger.info("Database reset completed successfully")
        return {"message": "Dados limpos com sucesso!", "database_type": "sqlite" if is_sqlite else "postgresql" if is_postgresql else "other"}
    except Exception as e:
        db.rollback()
        logger.error(f"Database reset failed: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao limpar dados: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
