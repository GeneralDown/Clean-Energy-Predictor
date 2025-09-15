"""
API routes for energy cleanliness predictions (live weather version).
"""

from fastapi import APIRouter, HTTPException, Query
from app.services.prediction import prediction_service  # use the service layer

router = APIRouter()

@router.get("/predictions")
async def get_predictions(
    location: str = Query(..., description="City name for predictions"),
    hours_ahead: int = Query(24, ge=1, le=168, description="Number of forecast hours (max 168 = 7 days)")
):
    """
    Get cleanliness prediction for a location using live weather data.
    """
    try:
        return await prediction_service.generate_predictions(location, hours_ahead=hours_ahead)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate predictions: {str(e)}")


@router.get("/predictions/{location}")
async def get_predictions_by_path(
    location: str,
    hours_ahead: int = Query(24, ge=1, le=168, description="Number of forecast hours (max 168 = 7 days)")
):
    """Alternative endpoint with location in path."""
    return await get_predictions(location=location, hours_ahead=hours_ahead)