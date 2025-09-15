"""
DataValidator class for validating environmental and grid data.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pydantic import ValidationError
import logging

from app.models.environmental import EnvironmentalData
from app.models.grid import GridData

logger = logging.getLogger(__name__)

class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.valid_records: List[Dict[str, Any]] = []
        self.invalid_records: List[Dict[str, Any]] = []
        self.errors: List[str] = []
    
    @property
    def is_valid(self) -> bool:
        """Check if all records are valid."""
        return len(self.invalid_records) == 0
    
    @property
    def total_records(self) -> int:
        """Total number of records processed."""
        return len(self.valid_records) + len(self.invalid_records)
    
    def add_valid_record(self, record: Dict[str, Any]):
        """Add a valid record."""
        self.valid_records.append(record)
    
    def add_invalid_record(self, record: Dict[str, Any], error: str):
        """Add an invalid record with error message."""
        self.invalid_records.append(record)
        self.errors.append(error)

class DataValidator:
    """
    Validates environmental and grid data against defined rules and schemas.
    """
    
    # Validation rules
    TEMPERATURE_RANGE = (-50, 60)  # Celsius
    CARBON_INTENSITY_RANGE = (0, 1000)  # gCO₂/kWh
    WIND_SPEED_RANGE = (0, 200)  # km/h
    AQI_RANGE = (0, 500)  # Air Quality Index
    PERCENTAGE_RANGE = (0, 100)  # Percentage values
    
    def __init__(self):
        """Initialize DataValidator."""
        pass
    
    def validate_environmental_data(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate environmental data records.
        
        Args:
            records: List of environmental data records
            
        Returns:
            ValidationResult containing valid/invalid records and errors
        """
        result = ValidationResult()
        
        for i, record in enumerate(records):
            try:
                # Check for required fields
                validation_errors = self._validate_environmental_record(record)
                
                if validation_errors:
                    error_msg = f"Record {i}: {'; '.join(validation_errors)}"
                    result.add_invalid_record(record, error_msg)
                    logger.warning(f"Invalid environmental record {i}: {validation_errors}")
                else:
                    # Parse timestamp if it's a string
                    if isinstance(record.get('timestamp'), str):
                        record['timestamp'] = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                    
                    # Validate using Pydantic model
                    env_data = EnvironmentalData(**record)
                    result.add_valid_record(record)
                    
            except ValidationError as e:
                error_msg = f"Record {i}: Pydantic validation failed - {str(e)}"
                result.add_invalid_record(record, error_msg)
                logger.warning(f"Environmental record {i} failed Pydantic validation: {e}")
            except Exception as e:
                error_msg = f"Record {i}: Unexpected validation error - {str(e)}"
                result.add_invalid_record(record, error_msg)
                logger.error(f"Unexpected error validating environmental record {i}: {e}")
        
        logger.info(f"Environmental validation complete: {len(result.valid_records)} valid, {len(result.invalid_records)} invalid")
        return result
    
    def validate_grid_data(self, records: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate grid data records.
        
        Args:
            records: List of grid data records
            
        Returns:
            ValidationResult containing valid/invalid records and errors
        """
        result = ValidationResult()
        
        for i, record in enumerate(records):
            try:
                # Check for required fields and custom validation
                validation_errors = self._validate_grid_record(record)
                
                if validation_errors:
                    error_msg = f"Record {i}: {'; '.join(validation_errors)}"
                    result.add_invalid_record(record, error_msg)
                    logger.warning(f"Invalid grid record {i}: {validation_errors}")
                else:
                    # Parse timestamp if it's a string
                    if isinstance(record.get('timestamp'), str):
                        record['timestamp'] = datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00'))
                    
                    # Map location to region for grid data
                    if 'location' in record and 'region' not in record:
                        record['region'] = record.pop('location')
                    
                    # Validate using Pydantic model
                    grid_data = GridData(**record)
                    result.add_valid_record(record)
                    
            except ValidationError as e:
                error_msg = f"Record {i}: Pydantic validation failed - {str(e)}"
                result.add_invalid_record(record, error_msg)
                logger.warning(f"Grid record {i} failed Pydantic validation: {e}")
            except Exception as e:
                error_msg = f"Record {i}: Unexpected validation error - {str(e)}"
                result.add_invalid_record(record, error_msg)
                logger.error(f"Unexpected error validating grid record {i}: {e}")
        
        logger.info(f"Grid validation complete: {len(result.valid_records)} valid, {len(result.invalid_records)} invalid")
        return result
    
    def _validate_environmental_record(self, record: Dict[str, Any]) -> List[str]:
        """
        Validate individual environmental record.
        
        Args:
            record: Environmental data record
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check required fields
        required_fields = ['timestamp', 'location']
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate timestamp
        if 'timestamp' in record and record['timestamp'] is not None:
            if not self._is_valid_timestamp(record['timestamp']):
                errors.append("Invalid timestamp format")
        
        # Validate location
        if 'location' in record and record['location'] is not None:
            if not isinstance(record['location'], str) or len(record['location'].strip()) == 0:
                errors.append("Location must be a non-empty string")
            elif len(record['location']) > 100:
                errors.append("Location must be 100 characters or less")
        
        # Validate temperature
        if 'temperature' in record and record['temperature'] is not None:
            temp = record['temperature']
            if not isinstance(temp, (int, float)):
                errors.append("Temperature must be a number")
            elif not (self.TEMPERATURE_RANGE[0] <= temp <= self.TEMPERATURE_RANGE[1]):
                errors.append(f"Temperature must be between {self.TEMPERATURE_RANGE[0]} and {self.TEMPERATURE_RANGE[1]} °C")
        
        # Validate wind speed
        if 'wind_speed' in record and record['wind_speed'] is not None:
            wind_speed = record['wind_speed']
            if not isinstance(wind_speed, (int, float)):
                errors.append("Wind speed must be a number")
            elif not (self.WIND_SPEED_RANGE[0] <= wind_speed <= self.WIND_SPEED_RANGE[1]):
                errors.append(f"Wind speed must be between {self.WIND_SPEED_RANGE[0]} and {self.WIND_SPEED_RANGE[1]} km/h")
        
        # Validate air quality index
        if 'air_quality_index' in record and record['air_quality_index'] is not None:
            aqi = record['air_quality_index']
            if not isinstance(aqi, int):
                errors.append("Air quality index must be an integer")
            elif not (self.AQI_RANGE[0] <= aqi <= self.AQI_RANGE[1]):
                errors.append(f"Air quality index must be between {self.AQI_RANGE[0]} and {self.AQI_RANGE[1]}")
        
        return errors
    
    def _validate_grid_record(self, record: Dict[str, Any]) -> List[str]:
        """
        Validate individual grid record.
        
        Args:
            record: Grid data record
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        # Check required fields
        required_fields = ['timestamp']
        location_field = 'location' if 'location' in record else 'region'
        required_fields.append(location_field)
        
        for field in required_fields:
            if field not in record or record[field] is None:
                errors.append(f"Missing required field: {field}")
        
        # Validate timestamp
        if 'timestamp' in record and record['timestamp'] is not None:
            if not self._is_valid_timestamp(record['timestamp']):
                errors.append("Invalid timestamp format")
        
        # Validate location/region
        location_value = record.get('location') or record.get('region')
        if location_value is not None:
            if not isinstance(location_value, str) or len(location_value.strip()) == 0:
                errors.append("Location/region must be a non-empty string")
            elif len(location_value) > 100:
                errors.append("Location/region must be 100 characters or less")
        
        # Validate carbon intensity
        if 'carbon_intensity' in record and record['carbon_intensity'] is not None:
            carbon_intensity = record['carbon_intensity']
            if not isinstance(carbon_intensity, (int, float)):
                errors.append("Carbon intensity must be a number")
            elif not (self.CARBON_INTENSITY_RANGE[0] <= carbon_intensity <= self.CARBON_INTENSITY_RANGE[1]):
                errors.append(f"Carbon intensity must be between {self.CARBON_INTENSITY_RANGE[0]} and {self.CARBON_INTENSITY_RANGE[1]} gCO₂/kWh")
        
        # Validate renewable percentage
        if 'renewable_percentage' in record and record['renewable_percentage'] is not None:
            renewable_pct = record['renewable_percentage']
            if not isinstance(renewable_pct, (int, float)):
                errors.append("Renewable percentage must be a number")
            elif not (self.PERCENTAGE_RANGE[0] <= renewable_pct <= self.PERCENTAGE_RANGE[1]):
                errors.append(f"Renewable percentage must be between {self.PERCENTAGE_RANGE[0]} and {self.PERCENTAGE_RANGE[1]}")
        
        return errors
    
    def _is_valid_timestamp(self, timestamp) -> bool:
        """
        Check if timestamp is valid.
        
        Args:
            timestamp: Timestamp value to validate
            
        Returns:
            True if valid, False otherwise
        """
        if isinstance(timestamp, datetime):
            return True
        
        if isinstance(timestamp, str):
            try:
                # Try parsing ISO format with Z suffix
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return True
            except ValueError:
                try:
                    # Try parsing other common formats
                    datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                    return True
                except ValueError:
                    return False
        
        return False