"""
Grid data models for the Clean Energy Predictor.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
import uuid

class GridDataDB(Base):
    """SQLAlchemy model for grid data."""
    __tablename__ = "grid_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    renewable_percentage = Column(Float, comment="Renewable energy percentage (0-100)")
    coal_percentage = Column(Float, comment="Coal energy percentage (0-100)")
    natural_gas_percentage = Column(Float, comment="Natural gas percentage (0-100)")
    nuclear_percentage = Column(Float, comment="Nuclear energy percentage (0-100)")
    total_demand = Column(Float, comment="Total energy demand in MW")
    carbon_intensity = Column(Float, comment="Carbon intensity in gCO2/kWh")
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    
    # Constraints
    __table_args__ = (
        CheckConstraint('renewable_percentage >= 0 AND renewable_percentage <= 100', name='check_renewable_percentage'),
        CheckConstraint('coal_percentage >= 0 AND coal_percentage <= 100', name='check_coal_percentage'),
        CheckConstraint('natural_gas_percentage >= 0 AND natural_gas_percentage <= 100', name='check_natural_gas_percentage'),
        CheckConstraint('nuclear_percentage >= 0 AND nuclear_percentage <= 100', name='check_nuclear_percentage'),
        CheckConstraint('total_demand >= 0', name='check_total_demand'),
        CheckConstraint('carbon_intensity >= 0', name='check_carbon_intensity'),
        Index('idx_grid_region_timestamp', 'region', 'timestamp'),
        Index('idx_grid_timestamp_desc', 'timestamp', postgresql_using='btree', postgresql_ops={'timestamp': 'DESC'}),
        Index('idx_grid_created_at', 'created_at'),
    )

class GridData(BaseModel):
    """Pydantic model for grid data validation."""
    timestamp: datetime
    region: str = Field(..., max_length=100)
    renewable_percentage: Optional[float] = Field(None, ge=0, le=100, description="Renewable energy percentage")
    coal_percentage: Optional[float] = Field(None, ge=0, le=100, description="Coal energy percentage")
    natural_gas_percentage: Optional[float] = Field(None, ge=0, le=100, description="Natural gas percentage")
    nuclear_percentage: Optional[float] = Field(None, ge=0, le=100, description="Nuclear energy percentage")
    total_demand: Optional[float] = Field(None, ge=0, description="Total energy demand in MW")
    carbon_intensity: Optional[float] = Field(None, ge=0, description="Carbon intensity in gCO2/kWh")

    @validator('renewable_percentage', 'coal_percentage', 'natural_gas_percentage', 'nuclear_percentage')
    def validate_percentages(cls, v, values):
        """Ensure energy mix percentages don't exceed 100% total."""
        if v is None:
            return v
        
        # Get all percentage values that are not None
        percentages = [
            values.get('renewable_percentage', 0) or 0,
            values.get('coal_percentage', 0) or 0,
            values.get('natural_gas_percentage', 0) or 0,
            values.get('nuclear_percentage', 0) or 0,
            v
        ]
        
        total = sum(p for p in percentages if p is not None)
        if total > 100:
            raise ValueError('Total energy mix percentages cannot exceed 100%')
        
        return v

class GridDataCreate(BaseModel):
    """Model for creating new grid data records."""
    region: str = Field(..., max_length=100)
    renewable_percentage: Optional[float] = None
    coal_percentage: Optional[float] = None
    natural_gas_percentage: Optional[float] = None
    nuclear_percentage: Optional[float] = None
    total_demand: Optional[float] = None
    carbon_intensity: Optional[float] = None

class GridDataResponse(GridData):
    """Response model including database ID."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True