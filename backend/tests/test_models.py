"""
Test cases for Pydantic models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.environmental import EnvironmentalData, EnvironmentalDataCreate
from app.models.grid import GridData, GridDataCreate
from app.models.prediction import PredictionPoint, ImpactMetrics

def test_environmental_data_validation():
    """Test environmental data model validation."""
    # Valid data
    valid_data = {
        "timestamp": datetime.utcnow(),
        "location": "test_location",
        "temperature": 25.5,
        "humidity": 60.0,
        "wind_speed": 15.2,
        "solar_irradiance": 800.0,
        "air_quality_index": 45
    }
    
    env_data = EnvironmentalData(**valid_data)
    assert env_data.location == "test_location"
    assert env_data.temperature == 25.5

def test_environmental_data_invalid_temperature():
    """Test environmental data with invalid temperature."""
    invalid_data = {
        "timestamp": datetime.utcnow(),
        "location": "test_location",
        "temperature": -100.0  # Too low
    }
    
    with pytest.raises(ValidationError):
        EnvironmentalData(**invalid_data)

def test_grid_data_validation():
    """Test grid data model validation."""
    valid_data = {
        "timestamp": datetime.utcnow(),
        "region": "test_region",
        "renewable_percentage": 35.2,
        "coal_percentage": 25.8,
        "natural_gas_percentage": 28.5,
        "nuclear_percentage": 10.5,
        "total_demand": 15000.0,
        "carbon_intensity": 420.5
    }
    
    grid_data = GridData(**valid_data)
    assert grid_data.region == "test_region"
    assert grid_data.renewable_percentage == 35.2

def test_prediction_point_validation():
    """Test prediction point model validation."""
    valid_data = {
        "timestamp": datetime.utcnow(),
        "cleanliness_score": 75.5,
        "confidence": 0.85,
        "carbon_intensity": 350.2
    }
    
    prediction = PredictionPoint(**valid_data)
    assert prediction.cleanliness_score == 75.5
    assert prediction.confidence == 0.85

def test_prediction_point_invalid_score():
    """Test prediction point with invalid score."""
    invalid_data = {
        "timestamp": datetime.utcnow(),
        "cleanliness_score": 150.0  # Too high
    }
    
    with pytest.raises(ValidationError):
        PredictionPoint(**invalid_data)

def test_impact_metrics_validation():
    """Test impact metrics model validation."""
    valid_data = {
        "co2_saved_kg": 2.5,
        "trees_equivalent": 5,
        "car_km_avoided": 20.8,
        "coal_plants_offset_hours": 0.003
    }
    
    impact = ImpactMetrics(**valid_data)
    assert impact.co2_saved_kg == 2.5
    assert impact.trees_equivalent == 5