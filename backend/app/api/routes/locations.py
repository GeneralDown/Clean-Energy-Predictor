"""
API routes for supported locations.
"""

from fastapi import APIRouter
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter()

class LocationInfo(BaseModel):
    """Information about a supported location."""
    code: str
    name: str
    region: str
    timezone: str
    supported_features: List[str]

class LocationsResponse(BaseModel):
    """Response model for supported locations."""
    locations: List[LocationInfo]
    total_count: int

@router.get("/locations", response_model=LocationsResponse)
async def get_supported_locations():
    """
    Get list of supported locations for predictions.
    
    Returns all locations where clean energy predictions are available.
    """
    # Mock data - in production, this would come from a database
    locations = [
        LocationInfo(
            code="default",
            name="Default Location",
            region="North America",
            timezone="UTC",
            supported_features=["predictions", "impact", "notifications"]
        ),
        LocationInfo(
            code="california",
            name="California, USA",
            region="North America",
            timezone="America/Los_Angeles",
            supported_features=["predictions", "impact", "notifications"]
        ),
        LocationInfo(
            code="texas",
            name="Texas, USA",
            region="North America",
            timezone="America/Chicago",
            supported_features=["predictions", "impact", "notifications"]
        ),
        LocationInfo(
            code="ontario",
            name="Ontario, Canada",
            region="North America",
            timezone="America/Toronto",
            supported_features=["predictions", "impact"]
        ),
        LocationInfo(
            code="germany",
            name="Germany",
            region="Europe",
            timezone="Europe/Berlin",
            supported_features=["predictions", "impact"]
        )
    ]
    
    return LocationsResponse(
        locations=locations,
        total_count=len(locations)
    )

@router.get("/locations/{location_code}")
async def get_location_info(location_code: str):
    """Get detailed information about a specific location."""
    locations_response = await get_supported_locations()
    
    for location in locations_response.locations:
        if location.code == location_code:
            return location
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail=f"Location '{location_code}' not found")