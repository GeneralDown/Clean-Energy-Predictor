"""
Prediction service using machine learning models for clean energy forecasting.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from app.models.prediction import PredictionPoint, PredictionsResponse, ImpactMetrics, ImpactResponse

logger = logging.getLogger(__name__)

class PredictionService:
    """Service for generating clean energy predictions."""
    
    def __init__(self):
        self.model_version = "1.0.0"
        self.is_trained = False
        
    def _generate_mock_predictions(self, location: str, hours: int = 24) -> List[PredictionPoint]:
        """Generate mock predictions for development."""
        predictions = []
        base_time = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        for i in range(hours):
            # Create realistic patterns: higher scores during midday (solar), lower at night
            hour = (base_time + timedelta(hours=i)).hour
            
            # Base score with daily pattern
            if 6 <= hour <= 18:  # Daytime
                base_score = 60 + 30 * np.sin((hour - 6) * np.pi / 12)
            else:  # Nighttime
                base_score = 40 + 20 * np.random.random()
            
            # Add some randomness
            score = max(0, min(100, base_score + np.random.normal(0, 10)))
            
            # Calculate carbon intensity (inverse relationship with cleanliness)
            carbon_intensity = 600 - (score * 4)  # Range: 200-600 gCO2/kWh
            
            prediction = PredictionPoint(
                timestamp=base_time + timedelta(hours=i),
                cleanliness_score=round(score, 1),
                confidence=round(0.7 + 0.3 * np.random.random(), 2),
                carbon_intensity=round(carbon_intensity, 1)
            )
            predictions.append(prediction)
            
        return predictions
    
    async def generate_predictions(self, location: str) -> PredictionsResponse:
        """Generate 24-hour predictions for a location."""
        try:
            logger.info(f"Generating predictions for location: {location}")
            
            # Generate predictions (mock implementation)
            predictions = self._generate_mock_predictions(location)
            
            response = PredictionsResponse(
                location=location,
                generated_at=datetime.utcnow(),
                predictions=predictions,
                model_version=self.model_version,
                data_freshness="< 15 minutes"
            )
            
            logger.info(f"Generated {len(predictions)} predictions for {location}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate predictions for {location}: {e}")
            raise
    
    def _calculate_impact_metrics(self, co2_saved_kg: float) -> ImpactMetrics:
        """Calculate relatable impact metrics from CO2 savings."""
        # Conversion factors
        TREE_CO2_ABSORPTION_KG_YEAR = 22  # kg CO2 per tree per year
        CAR_CO2_EMISSION_KG_KM = 0.12     # kg CO2 per km
        COAL_PLANT_CO2_KG_HOUR = 820000   # kg CO2 per hour for average coal plant
        
        trees_equivalent = int(co2_saved_kg * 365 / TREE_CO2_ABSORPTION_KG_YEAR)
        car_km_avoided = co2_saved_kg / CAR_CO2_EMISSION_KG_KM
        coal_plants_offset_hours = co2_saved_kg / COAL_PLANT_CO2_KG_HOUR
        
        return ImpactMetrics(
            co2_saved_kg=round(co2_saved_kg, 2),
            trees_equivalent=max(1, trees_equivalent),
            car_km_avoided=round(car_km_avoided, 1),
            coal_plants_offset_hours=round(coal_plants_offset_hours, 4)
        )
    
    async def calculate_impact(self, location: str, usage_kwh: float = 1.0) -> ImpactResponse:
        """Calculate environmental impact for energy usage."""
        try:
            logger.info(f"Calculating impact for {usage_kwh} kWh in {location}")
            
            # Get predictions to find cleanest and dirtiest hours
            predictions_response = await self.generate_predictions(location)
            predictions = predictions_response.predictions
            
            # Find cleanest and dirtiest hours
            cleanest = min(predictions, key=lambda p: p.carbon_intensity or 600)
            dirtiest = max(predictions, key=lambda p: p.carbon_intensity or 200)
            
            # Calculate CO2 emissions for each scenario
            cleanest_co2 = (cleanest.carbon_intensity or 200) * usage_kwh / 1000  # kg CO2
            dirtiest_co2 = (dirtiest.carbon_intensity or 600) * usage_kwh / 1000  # kg CO2
            co2_savings = dirtiest_co2 - cleanest_co2
            
            # Calculate impact metrics
            cleanest_impact = self._calculate_impact_metrics(cleanest_co2)
            dirtiest_impact = self._calculate_impact_metrics(dirtiest_co2)
            savings_impact = self._calculate_impact_metrics(co2_savings)
            
            response = ImpactResponse(
                location=location,
                usage_kwh=usage_kwh,
                cleanest_hour_impact=cleanest_impact,
                dirtiest_hour_impact=dirtiest_impact,
                potential_savings=savings_impact,
                calculation_timestamp=datetime.utcnow()
            )
            
            logger.info(f"Calculated impact: {co2_savings:.2f} kg CO2 savings potential")
            return response
            
        except Exception as e:
            logger.error(f"Failed to calculate impact for {location}: {e}")
            raise
    
    async def train_model(self, historical_data: pd.DataFrame) -> bool:
        """Train the prediction model with historical data."""
        try:
            logger.info("Training prediction model...")
            
            # Mock training implementation
            # In production, this would train Prophet/RandomForest models
            await asyncio.sleep(1)  # Simulate training time
            
            self.is_trained = True
            logger.info("Model training completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return False

# Global instance
prediction_service = PredictionService()