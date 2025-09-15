"""
API routes for environmental impact calculations.
"""

from fastapi import APIRouter, HTTPException, Query
from app.models.prediction import ImpactResponse
from app.services.prediction import prediction_service

router = APIRouter()

@router.get("/impact", response_model=ImpactResponse)
async def get_impact_metrics(
    location: str = Query("default", description="Location for impact calculation"),
    usage_kwh: float = Query(1.0, ge=0.1, le=1000.0, description="Energy usage in kWh")
):
    """
    Calculate environmental impact metrics for energy usage.
    
    Returns CO2 savings potential in relatable terms (trees planted, car km avoided, etc.)
    when using energy during cleanest vs dirtiest hours.
    """
    try:
        impact = await prediction_service.calculate_impact(location, usage_kwh)
        return impact
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate impact: {str(e)}")

@router.get("/impact/{location}")
async def get_impact_by_path(
    location: str,
    usage_kwh: float = Query(1.0, ge=0.1, le=1000.0, description="Energy usage in kWh")
):
    """Alternative endpoint with location in path."""
    return await get_impact_metrics(location=location, usage_kwh=usage_kwh)