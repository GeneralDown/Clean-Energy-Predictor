"""
Seed data for Clean Energy Predictor database.
"""

import logging
from datetime import datetime, timedelta
from typing import List
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.environmental import EnvironmentalDataDB
from app.models.grid import GridDataDB
from app.models.prediction import PredictionDB
from app.models.notification import NotificationSubscriptionDB, NotificationMethod

logger = logging.getLogger(__name__)

class SeedDataManager:
    """Manages database seed data for testing and development."""
    
    def __init__(self):
        self.locations = [
            "New York, NY",
            "Los Angeles, CA", 
            "Chicago, IL",
            "Houston, TX",
            "Phoenix, AZ",
            "Philadelphia, PA",
            "San Antonio, TX",
            "San Diego, CA",
            "Dallas, TX",
            "San Jose, CA"
        ]
        
        self.regions = [
            "NYISO",  # New York
            "CAISO",  # California
            "PJM",    # Pennsylvania, New Jersey, Maryland
            "ERCOT",  # Texas
            "MISO",   # Midwest
            "SPP",    # Southwest Power Pool
            "NEISO",  # New England
            "SERC",   # Southeast
        ]
    
    async def create_environmental_data(self, session: AsyncSession, days_back: int = 7) -> None:
        """Create sample environmental data."""
        logger.info(f"Creating environmental data for {days_back} days")
        
        base_time = datetime.utcnow() - timedelta(days=days_back)
        
        for location in self.locations:
            for hour in range(days_back * 24):
                timestamp = base_time + timedelta(hours=hour)
                
                # Generate realistic environmental data with some patterns
                hour_of_day = timestamp.hour
                day_of_year = timestamp.timetuple().tm_yday
                
                # Temperature varies by time of day and season
                base_temp = 15 + 10 * random.random()  # Base temperature
                seasonal_temp = 10 * (0.5 - abs(day_of_year - 182.5) / 365)  # Seasonal variation
                daily_temp = 5 * (0.5 - abs(hour_of_day - 14) / 24)  # Daily variation
                temperature = base_temp + seasonal_temp + daily_temp + random.gauss(0, 2)
                
                # Humidity inversely related to temperature
                humidity = max(20, min(95, 80 - temperature * 0.5 + random.gauss(0, 10)))
                
                # Wind speed varies randomly
                wind_speed = max(0, random.gauss(15, 8))
                
                # Solar irradiance depends on time of day
                if 6 <= hour_of_day <= 18:
                    solar_base = 800 * (1 - abs(hour_of_day - 12) / 6)
                    solar_irradiance = max(0, solar_base + random.gauss(0, 100))
                else:
                    solar_irradiance = 0
                
                # Air quality varies randomly but tends to be worse in urban areas
                aqi_base = 50 if "Los Angeles" in location or "Houston" in location else 30
                air_quality_index = max(0, min(300, int(aqi_base + random.gauss(0, 20))))
                
                env_data = EnvironmentalDataDB(
                    timestamp=timestamp,
                    location=location,
                    temperature=round(temperature, 1),
                    humidity=round(humidity, 1),
                    wind_speed=round(wind_speed, 1),
                    solar_irradiance=round(solar_irradiance, 1),
                    air_quality_index=air_quality_index
                )
                session.add(env_data)
        
        await session.commit()
        logger.info(f"Created environmental data for {len(self.locations)} locations")
    
    async def create_grid_data(self, session: AsyncSession, days_back: int = 7) -> None:
        """Create sample grid data."""
        logger.info(f"Creating grid data for {days_back} days")
        
        base_time = datetime.utcnow() - timedelta(days=days_back)
        
        for region in self.regions:
            for hour in range(days_back * 24):
                timestamp = base_time + timedelta(hours=hour)
                hour_of_day = timestamp.hour
                
                # Different regions have different energy mixes
                if region == "CAISO":  # California - high renewables
                    renewable_base = 40
                    coal_base = 5
                    gas_base = 35
                    nuclear_base = 15
                elif region == "ERCOT":  # Texas - high gas and wind
                    renewable_base = 25
                    coal_base = 15
                    gas_base = 45
                    nuclear_base = 10
                elif region == "PJM":  # Mid-Atlantic - mixed
                    renewable_base = 15
                    coal_base = 25
                    gas_base = 40
                    nuclear_base = 15
                else:  # Other regions
                    renewable_base = 20
                    coal_base = 20
                    gas_base = 40
                    nuclear_base = 15
                
                # Renewables higher during day (solar) and vary with wind
                renewable_variation = 15 if 8 <= hour_of_day <= 16 else -5
                renewable_percentage = max(0, min(80, renewable_base + renewable_variation + random.gauss(0, 10)))
                
                # Adjust other sources to maintain reasonable total
                remaining = 100 - renewable_percentage
                coal_percentage = max(0, min(remaining * 0.4, coal_base + random.gauss(0, 5)))
                remaining -= coal_percentage
                nuclear_percentage = max(0, min(remaining * 0.5, nuclear_base + random.gauss(0, 3)))
                remaining -= nuclear_percentage
                gas_percentage = max(0, remaining)
                
                # Total demand varies by time of day
                demand_base = 25000  # MW
                demand_variation = 5000 * (1 + 0.3 * (abs(hour_of_day - 12) / 12))  # Peak in afternoon
                total_demand = demand_base + demand_variation + random.gauss(0, 2000)
                
                # Carbon intensity based on energy mix
                carbon_intensity = (
                    renewable_percentage * 50 +  # Renewables: 50 gCO2/kWh
                    coal_percentage * 820 +      # Coal: 820 gCO2/kWh
                    gas_percentage * 490 +       # Natural gas: 490 gCO2/kWh
                    nuclear_percentage * 12      # Nuclear: 12 gCO2/kWh
                ) / 100
                
                grid_data = GridDataDB(
                    timestamp=timestamp,
                    region=region,
                    renewable_percentage=round(renewable_percentage, 1),
                    coal_percentage=round(coal_percentage, 1),
                    natural_gas_percentage=round(gas_percentage, 1),
                    nuclear_percentage=round(nuclear_percentage, 1),
                    total_demand=round(total_demand, 1),
                    carbon_intensity=round(carbon_intensity, 1)
                )
                session.add(grid_data)
        
        await session.commit()
        logger.info(f"Created grid data for {len(self.regions)} regions")
    
    async def create_predictions(self, session: AsyncSession, hours_ahead: int = 24) -> None:
        """Create sample prediction data."""
        logger.info(f"Creating predictions for {hours_ahead} hours ahead")
        
        base_time = datetime.utcnow()
        
        for location in self.locations:
            for hour in range(hours_ahead):
                target_timestamp = base_time + timedelta(hours=hour + 1)
                hour_of_day = target_timestamp.hour
                
                # Cleanliness score based on typical renewable patterns
                # Higher during day (solar), some randomness for wind
                if 8 <= hour_of_day <= 16:
                    base_score = 70 + 20 * (1 - abs(hour_of_day - 12) / 8)
                else:
                    base_score = 50 + random.random() * 30  # Wind variability
                
                cleanliness_score = max(0, min(100, base_score + random.gauss(0, 10)))
                confidence = max(0.5, min(1.0, 0.8 + random.gauss(0, 0.1)))
                
                # Carbon intensity inversely related to cleanliness
                carbon_intensity = 800 - (cleanliness_score * 6) + random.gauss(0, 50)
                carbon_intensity = max(200, carbon_intensity)
                
                prediction = PredictionDB(
                    location=location,
                    target_timestamp=target_timestamp,
                    cleanliness_score=round(cleanliness_score, 1),
                    confidence=round(confidence, 2),
                    carbon_intensity=round(carbon_intensity, 1),
                    model_version="v1.0.0"
                )
                session.add(prediction)
        
        await session.commit()
        logger.info(f"Created predictions for {len(self.locations)} locations")
    
    async def create_notification_subscriptions(self, session: AsyncSession) -> None:
        """Create sample notification subscriptions."""
        logger.info("Creating sample notification subscriptions")
        
        sample_emails = [
            "user1@example.com",
            "user2@example.com", 
            "user3@example.com",
            "test@cleanenergy.com",
            "demo@example.org"
        ]
        
        for i, email in enumerate(sample_emails):
            location = self.locations[i % len(self.locations)]
            
            subscription = NotificationSubscriptionDB(
                email=email,
                location=location,
                method=random.choice(list(NotificationMethod)),
                threshold_score=random.choice([60, 70, 80, 90]),
                advance_hours=random.choice([0.5, 1.0, 2.0, 4.0]),
                timezone=random.choice(["UTC", "America/New_York", "America/Los_Angeles", "America/Chicago"])
            )
            session.add(subscription)
        
        await session.commit()
        logger.info(f"Created {len(sample_emails)} notification subscriptions")
    
    async def seed_all(self, days_back: int = 7, hours_ahead: int = 24) -> None:
        """Seed all sample data."""
        logger.info("Starting database seeding process")
        
        async with AsyncSessionLocal() as session:
            try:
                await self.create_environmental_data(session, days_back)
                await self.create_grid_data(session, days_back)
                await self.create_predictions(session, hours_ahead)
                await self.create_notification_subscriptions(session)
                
                logger.info("Database seeding completed successfully")
            except Exception as e:
                logger.error(f"Database seeding failed: {e}")
                await session.rollback()
                raise
    
    async def clear_all_data(self) -> None:
        """Clear all seed data from database."""
        logger.info("Clearing all seed data")
        
        async with AsyncSessionLocal() as session:
            try:
                # Delete in reverse dependency order
                await session.execute("DELETE FROM notification_logs")
                await session.execute("DELETE FROM notification_subscriptions")
                await session.execute("DELETE FROM predictions")
                await session.execute("DELETE FROM grid_data")
                await session.execute("DELETE FROM environmental_data")
                
                await session.commit()
                logger.info("All seed data cleared successfully")
            except Exception as e:
                logger.error(f"Failed to clear seed data: {e}")
                await session.rollback()
                raise

# Global seed data manager instance
seed_manager = SeedDataManager()