"""
Multi-Armed Bandit Optimization API
Main FastAPI application with SQL integration
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func  # Adicione esta linha
from typing import List
import uvicorn

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

# Create database tables
Base.metadata.create_all(bind=engine)


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
