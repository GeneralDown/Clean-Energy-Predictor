"""
Unit tests for data ingestion service components.
"""

import pytest
import json
import tempfile
import asyncio
import sys
from pathlib import Path
from datetime import datetime
from unittest.mock import AsyncMock, patch, mock_open, MagicMock

# Mock the database dependencies before importing
sys.modules['asyncpg'] = MagicMock()
sys.modules['app.db.database'] = MagicMock()
sys.modules['app.models.environmental'] = MagicMock()
sys.modules['app.models.grid'] = MagicMock()

# Mock the Pydantic models
class MockEnvironmentalData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class MockGridData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Patch the imports
with patch.dict('sys.modules', {
    'app.models.environmental': MagicMock(EnvironmentalData=MockEnvironmentalData),
    'app.models.grid': MagicMock(GridData=MockGridData),
    'app.db.database': MagicMock()
}):
    from app.services.ingestion.data_fetcher import DataFetcher
    from app.services.ingestion.data_validator import DataValidator, ValidationResult

class TestDataFetcher:
    """Test cases for DataFetcher class."""
    
    @pytest.fixture
    def mock_environmental_data(self):
        """Mock environmental data for testing."""
        return [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Toronto",
                "temperature": -5.2,
                "wind_speed": 15.3,
                "air_quality_index": 42
            },
            {
                "timestamp": "2024-01-15T09:00:00Z",
                "location": "Vancouver",
                "temperature": 8.5,
                "wind_speed": 12.1,
                "air_quality_index": 25
            }
        ]
    
    @pytest.fixture
    def mock_grid_data(self):
        """Mock grid data for testing."""
        return [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Ontario",
                "carbon_intensity": 45.2,
                "renewable_percentage": 65.8
            },
            {
                "timestamp": "2024-01-15T09:00:00Z",
                "location": "British Columbia",
                "carbon_intensity": 12.5,
                "renewable_percentage": 92.1
            }
        ]
    
    @pytest.fixture
    def temp_mock_dir(self, mock_environmental_data, mock_grid_data):
        """Create temporary directory with mock data files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create environmental data file
            env_file = temp_path / "environmental_data.json"
            with open(env_file, 'w') as f:
                json.dump(mock_environmental_data, f)
            
            # Create grid data file
            grid_file = temp_path / "grid_data.json"
            with open(grid_file, 'w') as f:
                json.dump(mock_grid_data, f)
            
            yield temp_path
    
    def test_init_default_path(self):
        """Test DataFetcher initialization with default path."""
        fetcher = DataFetcher()
        assert fetcher.mock_data_path.name == "mock"
        assert fetcher.session is None
    
    def test_init_custom_path(self):
        """Test DataFetcher initialization with custom path."""
        custom_path = "/custom/path"
        fetcher = DataFetcher(custom_path)
        assert str(fetcher.mock_data_path) == custom_path
    
    @pytest.mark.asyncio
    async def test_fetch_environmental_data_mock(self, temp_mock_dir, mock_environmental_data):
        """Test fetching environmental data from mock files."""
        fetcher = DataFetcher(str(temp_mock_dir))
        
        data = await fetcher.fetch_environmental_data("mock")
        
        assert len(data) == 2
        assert data == mock_environmental_data
    
    @pytest.mark.asyncio
    async def test_fetch_grid_data_mock(self, temp_mock_dir, mock_grid_data):
        """Test fetching grid data from mock files."""
        fetcher = DataFetcher(str(temp_mock_dir))
        
        data = await fetcher.fetch_grid_data("mock")
        
        assert len(data) == 2
        assert data == mock_grid_data
    
    @pytest.mark.asyncio
    async def test_fetch_environmental_data_file_not_found(self):
        """Test error handling when mock file doesn't exist."""
        fetcher = DataFetcher("/nonexistent/path")
        
        with pytest.raises(FileNotFoundError):
            await fetcher.fetch_environmental_data("mock")
    
    @pytest.mark.asyncio
    async def test_fetch_grid_data_file_not_found(self):
        """Test error handling when mock file doesn't exist."""
        fetcher = DataFetcher("/nonexistent/path")
        
        with pytest.raises(FileNotFoundError):
            await fetcher.fetch_grid_data("mock")
    
    @pytest.mark.asyncio
    async def test_unsupported_source(self):
        """Test error handling for unsupported data source."""
        fetcher = DataFetcher()
        
        with pytest.raises(ValueError, match="Unsupported data source"):
            await fetcher.fetch_environmental_data("unsupported")
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test DataFetcher as async context manager."""
        async with DataFetcher() as fetcher:
            assert fetcher.session is not None
        
        # Session should be closed after exiting context
        assert fetcher.session.closed

class TestDataValidator:
    """Test cases for DataValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create DataValidator instance."""
        return DataValidator()
    
    @pytest.fixture
    def valid_environmental_records(self):
        """Valid environmental data records."""
        return [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Toronto",
                "temperature": -5.2,
                "wind_speed": 15.3,
                "air_quality_index": 42
            },
            {
                "timestamp": datetime(2024, 1, 15, 9, 0, 0),
                "location": "Vancouver",
                "temperature": 8.5,
                "wind_speed": 12.1,
                "air_quality_index": 25
            }
        ]
    
    @pytest.fixture
    def invalid_environmental_records(self):
        """Invalid environmental data records."""
        return [
            {
                # Missing timestamp
                "location": "Toronto",
                "temperature": -5.2
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                # Missing location
                "temperature": 100  # Invalid temperature
            },
            {
                "timestamp": "invalid-timestamp",
                "location": "Vancouver",
                "temperature": -60,  # Below minimum
                "wind_speed": -5,    # Negative wind speed
                "air_quality_index": 600  # Above maximum
            }
        ]
    
    @pytest.fixture
    def valid_grid_records(self):
        """Valid grid data records."""
        return [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Ontario",
                "carbon_intensity": 45.2,
                "renewable_percentage": 65.8
            },
            {
                "timestamp": datetime(2024, 1, 15, 9, 0, 0),
                "region": "British Columbia",
                "carbon_intensity": 12.5,
                "renewable_percentage": 92.1
            }
        ]
    
    @pytest.fixture
    def invalid_grid_records(self):
        """Invalid grid data records."""
        return [
            {
                # Missing timestamp
                "location": "Ontario",
                "carbon_intensity": 45.2
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                # Missing location/region
                "carbon_intensity": 1500  # Above maximum
            },
            {
                "timestamp": "invalid-timestamp",
                "location": "Quebec",
                "carbon_intensity": -10,  # Negative
                "renewable_percentage": 150  # Above 100%
            }
        ]
    
    def test_validate_environmental_data_valid(self, validator, valid_environmental_records):
        """Test validation of valid environmental data."""
        result = validator.validate_environmental_data(valid_environmental_records)
        
        assert result.is_valid
        assert len(result.valid_records) == 2
        assert len(result.invalid_records) == 0
        assert len(result.errors) == 0
    
    def test_validate_environmental_data_invalid(self, validator, invalid_environmental_records):
        """Test validation of invalid environmental data."""
        result = validator.validate_environmental_data(invalid_environmental_records)
        
        assert not result.is_valid
        assert len(result.valid_records) == 0
        assert len(result.invalid_records) == 3
        assert len(result.errors) == 3
    
    def test_validate_grid_data_valid(self, validator, valid_grid_records):
        """Test validation of valid grid data."""
        result = validator.validate_grid_data(valid_grid_records)
        
        assert result.is_valid
        assert len(result.valid_records) == 2
        assert len(result.invalid_records) == 0
        assert len(result.errors) == 0
    
    def test_validate_grid_data_invalid(self, validator, invalid_grid_records):
        """Test validation of invalid grid data."""
        result = validator.validate_grid_data(invalid_grid_records)
        
        assert not result.is_valid
        assert len(result.valid_records) == 0
        assert len(result.invalid_records) == 3
        assert len(result.errors) == 3
    
    def test_validate_empty_records(self, validator):
        """Test validation of empty record lists."""
        env_result = validator.validate_environmental_data([])
        grid_result = validator.validate_grid_data([])
        
        assert env_result.is_valid
        assert env_result.total_records == 0
        assert grid_result.is_valid
        assert grid_result.total_records == 0
    
    def test_temperature_range_validation(self, validator):
        """Test temperature range validation."""
        records = [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Arctic",
                "temperature": -60  # Below minimum
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Desert",
                "temperature": 70   # Above maximum
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Normal",
                "temperature": 25   # Valid
            }
        ]
        
        result = validator.validate_environmental_data(records)
        
        assert len(result.valid_records) == 1
        assert len(result.invalid_records) == 2
        assert "Temperature must be between" in result.errors[0]
        assert "Temperature must be between" in result.errors[1]
    
    def test_carbon_intensity_range_validation(self, validator):
        """Test carbon intensity range validation."""
        records = [
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Region1",
                "carbon_intensity": -10  # Below minimum
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Region2",
                "carbon_intensity": 1500  # Above maximum
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "location": "Region3",
                "carbon_intensity": 100   # Valid
            }
        ]
        
        result = validator.validate_grid_data(records)
        
        assert len(result.valid_records) == 1
        assert len(result.invalid_records) == 2

class TestDataStore:
    """Test cases for DataStore class."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def data_store(self, mock_session):
        """Create DataStore instance with mock session."""
        return DataStore(session=mock_session)
    
    @pytest.fixture
    def environmental_records(self):
        """Sample environmental records for testing."""
        return [
            {
                "timestamp": datetime(2024, 1, 15, 8, 0, 0),
                "location": "Toronto",
                "temperature": -5.2,
                "wind_speed": 15.3,
                "air_quality_index": 42
            },
            {
                "timestamp": datetime(2024, 1, 15, 9, 0, 0),
                "location": "Vancouver",
                "temperature": 8.5,
                "wind_speed": 12.1,
                "air_quality_index": 25
            }
        ]
    
    @pytest.fixture
    def grid_records(self):
        """Sample grid records for testing."""
        return [
            {
                "timestamp": datetime(2024, 1, 15, 8, 0, 0),
                "region": "Ontario",
                "carbon_intensity": 45.2,
                "renewable_percentage": 65.8
            },
            {
                "timestamp": datetime(2024, 1, 15, 9, 0, 0),
                "region": "British Columbia",
                "carbon_intensity": 12.5,
                "renewable_percentage": 92.1
            }
        ]
    
    @pytest.mark.asyncio
    async def test_store_environmental_data_success(self, data_store, environmental_records, mock_session):
        """Test successful storage of environmental data."""
        mock_session.execute.return_value = AsyncMock()
        mock_session.commit.return_value = AsyncMock()
        
        result = await data_store.store_environmental_data(environmental_records)
        
        assert result == 2
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_grid_data_success(self, data_store, grid_records, mock_session):
        """Test successful storage of grid data."""
        mock_session.execute.return_value = AsyncMock()
        mock_session.commit.return_value = AsyncMock()
        
        result = await data_store.store_grid_data(grid_records)
        
        assert result == 2
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_empty_records(self, data_store):
        """Test storing empty record lists."""
        env_result = await data_store.store_environmental_data([])
        grid_result = await data_store.store_grid_data([])
        
        assert env_result == 0
        assert grid_result == 0
    
    @pytest.mark.asyncio
    async def test_store_environmental_data_database_error(self, data_store, environmental_records, mock_session):
        """Test database error handling during environmental data storage."""
        from sqlalchemy.exc import SQLAlchemyError
        
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = AsyncMock()
        
        with pytest.raises(SQLAlchemyError):
            await data_store.store_environmental_data(environmental_records)
        
        mock_session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_grid_data_database_error(self, data_store, grid_records, mock_session):
        """Test database error handling during grid data storage."""
        from sqlalchemy.exc import SQLAlchemyError
        
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        mock_session.rollback.return_value = AsyncMock()
        
        with pytest.raises(SQLAlchemyError):
            await data_store.store_grid_data(grid_records)
        
        mock_session.rollback.assert_called_once()

class TestValidationResult:
    """Test cases for ValidationResult class."""
    
    def test_init(self):
        """Test ValidationResult initialization."""
        result = ValidationResult()
        
        assert result.valid_records == []
        assert result.invalid_records == []
        assert result.errors == []
        assert result.is_valid is True
        assert result.total_records == 0
    
    def test_add_valid_record(self):
        """Test adding valid records."""
        result = ValidationResult()
        record = {"test": "data"}
        
        result.add_valid_record(record)
        
        assert len(result.valid_records) == 1
        assert result.valid_records[0] == record
        assert result.is_valid is True
        assert result.total_records == 1
    
    def test_add_invalid_record(self):
        """Test adding invalid records."""
        result = ValidationResult()
        record = {"test": "data"}
        error = "Test error"
        
        result.add_invalid_record(record, error)
        
        assert len(result.invalid_records) == 1
        assert len(result.errors) == 1
        assert result.invalid_records[0] == record
        assert result.errors[0] == error
        assert result.is_valid is False
        assert result.total_records == 1
    
    def test_mixed_records(self):
        """Test with both valid and invalid records."""
        result = ValidationResult()
        
        result.add_valid_record({"valid": "data"})
        result.add_invalid_record({"invalid": "data"}, "Error message")
        
        assert len(result.valid_records) == 1
        assert len(result.invalid_records) == 1
        assert len(result.errors) == 1
        assert result.is_valid is False
        assert result.total_records == 2