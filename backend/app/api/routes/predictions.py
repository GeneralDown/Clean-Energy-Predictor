"""
API routes for energy cleanliness predictions (live weather version).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services.prediction import prediction_service

router = APIRouter()

@router.get("/predictions")
async def get_predictions(
    location: str = Query(..., description="City name for predictions"),
    hours_ahead: int = Query(24, ge=1, le=168, description="Number of forecast hours (max 168 = 7 days)"),
    day: Optional[str] = Query(None, description="Target day in YYYY-MM-DD format"),
    duration_hours: int = Query(1, ge=1, le=24, description="Duration of activity in hours")
):
    """
    Get cleanliness prediction for a location, optionally for a specific day and duration.
    """
    try:
        return await prediction_service.generate_predictions(
            location=location,
            hours_ahead=hours_ahead,
            day=day,
            duration_hours=duration_hours
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate predictions: {str(e)}")


@router.get("/predictions/{location}")
async def get_predictions_by_path(
    location: str,
    hours_ahead: int = Query(24, ge=1, le=168),
    day: Optional[str] = Query(None),
    duration_hours: int = Query(1, ge=1, le=24)
):
    """Alternative endpoint with location in path."""
    return await get_predictions(
        location=location,
        hours_ahead=hours_ahead,
        day=day,
        duration_hours=duration_hours
    )