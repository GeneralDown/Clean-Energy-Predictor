"""
Prediction models for the Clean Energy Predictor.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy import Index, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
import uuid

class PredictionDB(Base):
    """SQLAlchemy model for predictions."""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    location = Column(String(100), nullable=False, index=True)
    prediction_timestamp = Column(DateTime(timezone=True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    target_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    cleanliness_score = Column(Float, nullable=False, comment="Cleanliness score from 0-100")
    confidence = Column(Float, comment="Prediction confidence from 0-1")
    model_version = Column(String(50), comment="Version of the prediction model used")
    carbon_intensity = Column(Float, comment="Predicted carbon intensity in gCO2/kWh")
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    
    # Constraints and indexes
    __table_args__ = (
        CheckConstraint('cleanliness_score >= 0 AND cleanliness_score <= 100', name='check_cleanliness_score'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence'),
        CheckConstraint('carbon_intensity >= 0', name='check_carbon_intensity'),
        Index('idx_pred_location_target', 'location', 'target_timestamp'),
        Index('idx_pred_target_desc', 'target_timestamp', postgresql_using='btree', postgresql_ops={'target_timestamp': 'DESC'}),
        Index('idx_pred_created_at', 'created_at'),
    )

class PredictionPoint(BaseModel):
    """Individual prediction point model."""
    timestamp: datetime
    cleanliness_score: float = Field(..., ge=0, le=100, description="Cleanliness score from 0-100")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Prediction confidence 0-1")
    carbon_intensity: Optional[float] = Field(None, ge=0, description="Carbon intensity in gCO2/kWh")

class PredictionsResponse(BaseModel):
    """Response model for 24-hour predictions."""
    location: str
    generated_at: datetime
    predictions: List[PredictionPoint] = Field(..., min_items=24, max_items=24)
    model_version: Optional[str] = None
    data_freshness: Optional[str] = Field(None, description="Age of underlying data")

class PredictionCreate(BaseModel):
    """Model for creating new prediction records."""
    location: str = Field(..., max_length=100)
    target_timestamp: datetime
    cleanliness_score: float = Field(..., ge=0, le=100)
    confidence: Optional[float] = Field(None, ge=0, le=1)
    model_version: Optional[str] = None

class PredictionResponse(BaseModel):
    """Response model for individual predictions."""
    id: int
    location: str
    prediction_timestamp: datetime
    target_timestamp: datetime
    cleanliness_score: float
    confidence: Optional[float]
    model_version: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImpactMetrics(BaseModel):
    """Environmental impact metrics model."""
    co2_saved_kg: float = Field(..., description="CO2 saved in kilograms")
    trees_equivalent: int = Field(..., description="Equivalent number of trees planted")
    car_km_avoided: float = Field(..., description="Car kilometers avoided")
    coal_plants_offset_hours: float = Field(..., description="Coal plant hours offset")

class ImpactResponse(BaseModel):
    """Response model for impact calculations."""
    location: str
    usage_kwh: float
    cleanest_hour_impact: ImpactMetrics
    dirtiest_hour_impact: ImpactMetrics
    potential_savings: ImpactMetrics
    calculation_timestamp: datetime