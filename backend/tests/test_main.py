"""
Test cases for the main FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Clean Energy Predictor API"
    assert data["version"] == "1.0.0"

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_predictions_endpoint():
    """Test the predictions endpoint."""
    response = client.get("/api/v1/predictions")
    assert response.status_code == 200
    data = response.json()
    assert "location" in data
    assert "predictions" in data
    assert len(data["predictions"]) == 24

def test_impact_endpoint():
    """Test the impact endpoint."""
    response = client.get("/api/v1/impact?usage_kwh=2.0")
    assert response.status_code == 200
    data = response.json()
    assert "location" in data
    assert "usage_kwh" in data
    assert data["usage_kwh"] == 2.0

def test_locations_endpoint():
    """Test the locations endpoint."""
    response = client.get("/api/v1/locations")
    assert response.status_code == 200
    data = response.json()
    assert "locations" in data
    assert "total_count" in data
    assert len(data["locations"]) > 0