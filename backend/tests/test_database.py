"""
Tests for database functionality.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_test_db, create_test_tables, drop_test_tables
from app.models.environmental import EnvironmentalDataDB
from app.models.grid import GridDataDB
from app.models.prediction import PredictionDB
from app.models.notification import NotificationSubscriptionDB, NotificationMethod

@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up test database tables."""
    await create_test_tables()
    yield
    await drop_test_tables()

@pytest.fixture
async def db_session():
    """Get test database session."""
    async for session in get_test_db():
        yield session

@pytest.mark.asyncio
async def test_environmental_data_crud(db_session: AsyncSession):
    """Test environmental data CRUD operations."""
    # Create
    env_data = EnvironmentalDataDB(
        timestamp=datetime.utcnow(),
        location="Test City",
        temperature=25.5,
        humidity=60.0,
        wind_speed=15.0,
        solar_irradiance=800.0,
        air_quality_index=50
    )
    db_session.add(env_data)
    await db_session.commit()
    await db_session.refresh(env_data)
    
    # Read
    assert env_data.id is not None
    assert env_data.location == "Test City"
    assert env_data.temperature == 25.5
    
    # Update
    env_data.temperature = 26.0
    await db_session.commit()
    await db_session.refresh(env_data)
    assert env_data.temperature == 26.0
    
    # Delete
    await db_session.delete(env_data)
    await db_session.commit()

@pytest.mark.asyncio
async def test_grid_data_crud(db_session: AsyncSession):
    """Test grid data CRUD operations."""
    # Create
    grid_data = GridDataDB(
        timestamp=datetime.utcnow(),
        region="TEST_REGION",
        renewable_percentage=45.0,
        coal_percentage=20.0,
        natural_gas_percentage=25.0,
        nuclear_percentage=10.0,
        total_demand=25000.0,
        carbon_intensity=400.0
    )
    db_session.add(grid_data)
    await db_session.commit()
    await db_session.refresh(grid_data)
    
    # Read
    assert grid_data.id is not None
    assert grid_data.region == "TEST_REGION"
    assert grid_data.renewable_percentage == 45.0
    
    # Delete
    await db_session.delete(grid_data)
    await db_session.commit()

@pytest.mark.asyncio
async def test_prediction_crud(db_session: AsyncSession):
    """Test prediction CRUD operations."""
    # Create
    prediction = PredictionDB(
        location="Test City",
        target_timestamp=datetime.utcnow() + timedelta(hours=1),
        cleanliness_score=75.5,
        confidence=0.85,
        carbon_intensity=350.0,
        model_version="v1.0.0"
    )
    db_session.add(prediction)
    await db_session.commit()
    await db_session.refresh(prediction)
    
    # Read
    assert prediction.id is not None
    assert prediction.location == "Test City"
    assert prediction.cleanliness_score == 75.5
    assert prediction.confidence == 0.85
    
    # Delete
    await db_session.delete(prediction)
    await db_session.commit()

@pytest.mark.asyncio
async def test_notification_subscription_crud(db_session: AsyncSession):
    """Test notification subscription CRUD operations."""
    # Create
    subscription = NotificationSubscriptionDB(
        email="test@example.com",
        location="Test City",
        method=NotificationMethod.EMAIL,
        threshold_score=70.0,
        advance_hours=1.0,
        timezone="UTC"
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)
    
    # Read
    assert subscription.id is not None
    assert subscription.email == "test@example.com"
    assert subscription.location == "Test City"
    assert subscription.method == NotificationMethod.EMAIL
    assert subscription.is_active is True
    
    # Update
    subscription.threshold_score = 80.0
    subscription.is_active = False
    await db_session.commit()
    await db_session.refresh(subscription)
    assert subscription.threshold_score == 80.0
    assert subscription.is_active is False
    
    # Delete
    await db_session.delete(subscription)
    await db_session.commit()

@pytest.mark.asyncio
async def test_database_constraints(db_session: AsyncSession):
    """Test database constraints."""
    # Test cleanliness score constraint
    with pytest.raises(Exception):  # Should raise constraint violation
        prediction = PredictionDB(
            location="Test City",
            target_timestamp=datetime.utcnow() + timedelta(hours=1),
            cleanliness_score=150.0,  # Invalid: > 100
            confidence=0.85,
            model_version="v1.0.0"
        )
        db_session.add(prediction)
        await db_session.commit()
    
    await db_session.rollback()
    
    # Test confidence constraint
    with pytest.raises(Exception):  # Should raise constraint violation
        prediction = PredictionDB(
            location="Test City",
            target_timestamp=datetime.utcnow() + timedelta(hours=1),
            cleanliness_score=75.0,
            confidence=1.5,  # Invalid: > 1.0
            model_version="v1.0.0"
        )
        db_session.add(prediction)
        await db_session.commit()
    
    await db_session.rollback()

@pytest.mark.asyncio
async def test_database_indexes(db_session: AsyncSession):
    """Test that database indexes work correctly."""
    # Create test data
    base_time = datetime.utcnow()
    
    for i in range(10):
        env_data = EnvironmentalDataDB(
            timestamp=base_time + timedelta(hours=i),
            location=f"City_{i % 3}",  # 3 different cities
            temperature=20.0 + i,
            humidity=50.0,
            wind_speed=10.0,
            solar_irradiance=500.0,
            air_quality_index=40
        )
        db_session.add(env_data)
    
    await db_session.commit()
    
    # Test location-based query (should use index)
    from sqlalchemy import select
    result = await db_session.execute(
        select(EnvironmentalDataDB).where(EnvironmentalDataDB.location == "City_0")
    )
    city_0_data = result.scalars().all()
    assert len(city_0_data) > 0
    
    # Test timestamp-based query (should use index)
    result = await db_session.execute(
        select(EnvironmentalDataDB).where(
            EnvironmentalDataDB.timestamp >= base_time + timedelta(hours=5)
        )
    )
    recent_data = result.scalars().all()
    assert len(recent_data) == 5  # Last 5 records