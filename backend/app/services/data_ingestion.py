"""
Data ingestion service for fetching external environmental and grid data.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import httpx
from app.models.environmental import EnvironmentalData, EnvironmentalDataCreate
from app.models.grid import GridData, GridDataCreate

logger = logging.getLogger(__name__)

class DataIngestionService:
    """Service for ingesting data from external APIs."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.retry_attempts = 3
        self.retry_delay = 1.0  # seconds
    
    async def fetch_environmental_data(self, location: str) -> Optional[EnvironmentalDataCreate]:
        """Fetch environmental data from external APIs."""
        try:
            # Mock implementation - replace with actual API calls
            # Example: OpenWeatherMap, EPA Air Quality API
            
            # Simulate API call with retry logic
            for attempt in range(self.retry_attempts):
                try:
                    # Mock data for development
                    mock_data = {
                        "location": location,
                        "temperature": 22.5,
                        "humidity": 65.0,
                        "wind_speed": 15.2,
                        "solar_irradiance": 800.0,
                        "air_quality_index": 45
                    }
                    
                    return EnvironmentalDataCreate(**mock_data)
                    
                except httpx.RequestError as e:
                    logger.warning(f"Attempt {attempt + 1} failed for environmental data: {e}")
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Failed to fetch environmental data for {location}: {e}")
            return None
    
    async def fetch_grid_data(self, region: str) -> Optional[GridDataCreate]:
        """Fetch grid data from external APIs."""
        try:
            # Mock implementation - replace with actual API calls
            # Example: EIA API, regional grid operators
            
            for attempt in range(self.retry_attempts):
                try:
                    # Mock data for development
                    mock_data = {
                        "region": region,
                        "renewable_percentage": 35.2,
                        "coal_percentage": 25.8,
                        "natural_gas_percentage": 28.5,
                        "nuclear_percentage": 10.5,
                        "total_demand": 15000.0,
                        "carbon_intensity": 420.5
                    }
                    
                    return GridDataCreate(**mock_data)
                    
                except httpx.RequestError as e:
                    logger.warning(f"Attempt {attempt + 1} failed for grid data: {e}")
                    if attempt < self.retry_attempts - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    else:
                        raise
                        
        except Exception as e:
            logger.error(f"Failed to fetch grid data for {region}: {e}")
            return None
    
    async def ingest_data_for_location(self, location: str) -> Dict[str, bool]:
        """Ingest both environmental and grid data for a location."""
        results = {"environmental": False, "grid": False}
        
        # Fetch environmental data
        env_data = await self.fetch_environmental_data(location)
        if env_data:
            # TODO: Store in database
            results["environmental"] = True
            logger.info(f"Successfully ingested environmental data for {location}")
        
        # Fetch grid data (assuming location maps to region)
        grid_data = await self.fetch_grid_data(location)
        if grid_data:
            # TODO: Store in database
            results["grid"] = True
            logger.info(f"Successfully ingested grid data for {location}")
        
        return results
    
    async def run_ingestion_cycle(self, locations: List[str]) -> Dict[str, Dict[str, bool]]:
        """Run a complete data ingestion cycle for all locations."""
        logger.info(f"Starting ingestion cycle for {len(locations)} locations")
        
        results = {}
        tasks = [self.ingest_data_for_location(location) for location in locations]
        
        try:
            ingestion_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for location, result in zip(locations, ingestion_results):
                if isinstance(result, Exception):
                    logger.error(f"Ingestion failed for {location}: {result}")
                    results[location] = {"environmental": False, "grid": False}
                else:
                    results[location] = result
                    
        except Exception as e:
            logger.error(f"Ingestion cycle failed: {e}")
            
        logger.info(f"Ingestion cycle completed. Results: {results}")
        return results
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Global instance
data_ingestion_service = DataIngestionService()