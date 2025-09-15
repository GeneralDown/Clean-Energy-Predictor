"""
Environmental data models for the Clean Energy Predictor.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base
import uuid

class EnvironmentalDataDB(Base):
    """SQLAlchemy model for environmental data."""
    __tablename__ = "environmental_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    location = Column(String(100), nullable=False, index=True)
    temperature = Column(Float, comment="Temperature in Celsius")
    humidity = Column(Float, comment="Humidity percentage (0-100)")
    wind_speed = Column(Float, comment="Wind speed in km/h")
    solar_irradiance = Column(Float, comment="Solar irradiance in W/m²")
    air_quality_index = Column(Integer, comment="Air Quality Index (0-500)")
    created_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_env_location_timestamp', 'location', 'timestamp'),
        Index('idx_env_timestamp_desc', 'timestamp', postgresql_using='btree', postgresql_ops={'timestamp': 'DESC'}),
        Index('idx_env_created_at', 'created_at'),
    )

class EnvironmentalData(BaseModel):
    """Pydantic model for environmental data validation."""
    timestamp: datetime
    location: str = Field(..., max_length=100)
    temperature: Optional[float] = Field(None, ge=-50, le=60, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, ge=0, le=100, description="Humidity percentage")
    wind_speed: Optional[float] = Field(None, ge=0, le=200, description="Wind speed in km/h")
    solar_irradiance: Optional[float] = Field(None, ge=0, description="Solar irradiance in W/m²")
    air_quality_index: Optional[int] = Field(None, ge=0, le=500, description="Air Quality Index")

class EnvironmentalDataCreate(BaseModel):
    """Model for creating new environmental data records."""
    location: str = Field(..., max_length=100)
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    solar_irradiance: Optional[float] = None
    air_quality_index: Optional[int] = None

class EnvironmentalDataResponse(EnvironmentalData):
    """Response model including database ID."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True