"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime

class ExperimentCreate(BaseModel):
    """Schema for creating a new experiment"""
    name: str
    description: Optional[str] = None

class MetricItem(BaseModel):
    """Schema for individual metric item"""
    date: Optional[str]
    variant_name: str
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    
    class Config:
        from_attributes = True

class ExperimentResponse(BaseModel):
    """Schema for experiment response"""
    id: int
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    metrics: Optional[List[Dict[str, Any]]] = []
    
    class Config:
        from_attributes = True

class VariantData(BaseModel):
    """Schema for individual variant performance data"""
    name: str
    impressions: int
    clicks: int
    conversions: Optional[int] = 0
    
    @validator('clicks')
    def clicks_not_greater_than_impressions(cls, v, values):
        if 'impressions' in values and v > values['impressions']:
            raise ValueError('clicks cannot be greater than impressions')
        return v
    
    @validator('conversions')
    def conversions_not_greater_than_clicks(cls, v, values):
        if 'clicks' in values and v > values['clicks']:
            raise ValueError('conversions cannot be greater than clicks')
        return v

class MetricDataCreate(BaseModel):
    """Schema for submitting experiment metric data"""
    date: date
    variants: List[VariantData]
    
    @validator('variants')
    def variants_not_empty(cls, v):
        if not v:
            raise ValueError('at least one variant must be provided')
        return v

class MetricDataResponse(BaseModel):
    """Schema for metric data submission response"""
    experiment_id: int
    date: date
    variants_processed: int
    total_impressions: int
    total_clicks: int

class VariantAllocation(BaseModel):
    """Schema for individual variant allocation"""
    variant: str
    allocation: float
    ctr: float
    impressions: int
    clicks: int

class AllocationResponse(BaseModel):
    """Schema for allocation calculation response"""
    allocations: Dict[str, float]
    algorithm: str
    parameters: Dict[str, Any]
    experiment_id: int
    window_days: int
    timestamp: str
