"""
DataStore class for storing validated data in PostgreSQL database.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

from app.models.environmental import EnvironmentalDataDB
from app.models.grid import GridDataDB
from app.db.database import get_db

logger = logging.getLogger(__name__)

class DataStore:
    """
    Handles CRUD operations for environmental and grid data in PostgreSQL.
    """
    
    def __init__(self, session: Optional[AsyncSession] = None):
        """
        Initialize DataStore.
        
        Args:
            session: Optional database session. If not provided, will use dependency injection.
        """
        self.session = session
    
    async def store_environmental_data(self, records: List[Dict[str, Any]]) -> int:
        """
        Store environmental data records in the database.
        
        Args:
            records: List of validated environmental data records
            
        Returns:
            Number of records successfully stored
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        if not records:
            logger.info("No environmental records to store")
            return 0
        
        stored_count = 0
        session = self.session
        
        try:
            if session is None:
                # Use dependency injection to get session
                async for db_session in get_db():
                    session = db_session
                    break
            
            # Prepare records for insertion
            db_records = []
            for record in records:
                db_record = {
                    'timestamp': record['timestamp'],
                    'location': record['location'],
                    'temperature': record.get('temperature'),
                    'wind_speed': record.get('wind_speed'),
                    'air_quality_index': record.get('air_quality_index'),
                    'humidity': record.get('humidity'),
                    'solar_irradiance': record.get('solar_irradiance')
                }
                db_records.append(db_record)
            
            # Bulk insert
            stmt = insert(EnvironmentalDataDB).values(db_records)
            result = await session.execute(stmt)
            await session.commit()
            
            stored_count = len(db_records)
            logger.info(f"Successfully stored {stored_count} environmental records")
            
        except SQLAlchemyError as e:
            if session:
                await session.rollback()
            logger.error(f"Database error storing environmental data: {e}")
            raise
        except Exception as e:
            if session:
                await session.rollback()
            logger.error(f"Unexpected error storing environmental data: {e}")
            raise
        
        return stored_count
    
    async def store_grid_data(self, records: List[Dict[str, Any]]) -> int:
        """
        Store grid data records in the database.
        
        Args:
            records: List of validated grid data records
            
        Returns:
            Number of records successfully stored
            
        Raises:
            SQLAlchemyError: If database operation fails
        """
        if not records:
            logger.info("No grid records to store")
            return 0
        
        stored_count = 0
        session = self.session
        
        try:
            if session is None:
                # Use dependency injection to get session
                async for db_session in get_db():
                    session = db_session
                    break
            
            # Prepare records for insertion
            db_records = []
            for record in records:
                db_record = {
                    'timestamp': record['timestamp'],
                    'region': record['region'],
                    'carbon_intensity': record.get('carbon_intensity'),
                    'renewable_percentage': record.get('renewable_percentage'),
                    'coal_percentage': record.get('coal_percentage'),
                    'natural_gas_percentage': record.get('natural_gas_percentage'),
                    'nuclear_percentage': record.get('nuclear_percentage'),
                    'total_demand': record.get('total_demand')
                }
                db_records.append(db_record)
            
            # Bulk insert
            stmt = insert(GridDataDB).values(db_records)
            result = await session.execute(stmt)
            await session.commit()
            
            stored_count = len(db_records)
            logger.info(f"Successfully stored {stored_count} grid records")
            
        except SQLAlchemyError as e:
            if session:
                await session.rollback()
            logger.error(f"Database error storing grid data: {e}")
            raise
        except Exception as e:
            if session:
                await session.rollback()
            logger.error(f"Unexpected error storing grid data: {e}")
            raise
        
        return stored_count
    
    async def get_environmental_data(
        self, 
        location: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve environmental data from the database.
        
        Args:
            location: Filter by location
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            limit: Maximum number of records to return
            
        Returns:
            List of environmental data records
        """
        session = self.session
        
        try:
            if session is None:
                async for db_session in get_db():
                    session = db_session
                    break
            
            # Build query
            query = select(EnvironmentalDataDB)
            
            if location:
                query = query.where(EnvironmentalDataDB.location == location)
            if start_time:
                query = query.where(EnvironmentalDataDB.timestamp >= start_time)
            if end_time:
                query = query.where(EnvironmentalDataDB.timestamp <= end_time)
            
            query = query.order_by(EnvironmentalDataDB.timestamp.desc()).limit(limit)
            
            result = await session.execute(query)
            records = result.scalars().all()
            
            # Convert to dictionaries
            data = []
            for record in records:
                data.append({
                    'id': str(record.id),
                    'timestamp': record.timestamp,
                    'location': record.location,
                    'temperature': record.temperature,
                    'humidity': record.humidity,
                    'wind_speed': record.wind_speed,
                    'solar_irradiance': record.solar_irradiance,
                    'air_quality_index': record.air_quality_index,
                    'created_at': record.created_at
                })
            
            logger.info(f"Retrieved {len(data)} environmental records")
            return data
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving environmental data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving environmental data: {e}")
            raise
    
    async def get_grid_data(
        self,
        region: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve grid data from the database.
        
        Args:
            region: Filter by region
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            limit: Maximum number of records to return
            
        Returns:
            List of grid data records
        """
        session = self.session
        
        try:
            if session is None:
                async for db_session in get_db():
                    session = db_session
                    break
            
            # Build query
            query = select(GridDataDB)
            
            if region:
                query = query.where(GridDataDB.region == region)
            if start_time:
                query = query.where(GridDataDB.timestamp >= start_time)
            if end_time:
                query = query.where(GridDataDB.timestamp <= end_time)
            
            query = query.order_by(GridDataDB.timestamp.desc()).limit(limit)
            
            result = await session.execute(query)
            records = result.scalars().all()
            
            # Convert to dictionaries
            data = []
            for record in records:
                data.append({
                    'id': str(record.id),
                    'timestamp': record.timestamp,
                    'region': record.region,
                    'renewable_percentage': record.renewable_percentage,
                    'coal_percentage': record.coal_percentage,
                    'natural_gas_percentage': record.natural_gas_percentage,
                    'nuclear_percentage': record.nuclear_percentage,
                    'total_demand': record.total_demand,
                    'carbon_intensity': record.carbon_intensity,
                    'created_at': record.created_at
                })
            
            logger.info(f"Retrieved {len(data)} grid records")
            return data
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving grid data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error retrieving grid data: {e}")
            raise
    
    async def delete_environmental_data(self, record_ids: List[str]) -> int:
        """
        Delete environmental data records by IDs.
        
        Args:
            record_ids: List of record IDs to delete
            
        Returns:
            Number of records deleted
        """
        if not record_ids:
            return 0
        
        session = self.session
        
        try:
            if session is None:
                async for db_session in get_db():
                    session = db_session
                    break
            
            stmt = delete(EnvironmentalDataDB).where(EnvironmentalDataDB.id.in_(record_ids))
            result = await session.execute(stmt)
            await session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} environmental records")
            return deleted_count
            
        except SQLAlchemyError as e:
            if session:
                await session.rollback()
            logger.error(f"Database error deleting environmental data: {e}")
            raise
        except Exception as e:
            if session:
                await session.rollback()
            logger.error(f"Unexpected error deleting environmental data: {e}")
            raise
    
    async def delete_grid_data(self, record_ids: List[str]) -> int:
        """
        Delete grid data records by IDs.
        
        Args:
            record_ids: List of record IDs to delete
            
        Returns:
            Number of records deleted
        """
        if not record_ids:
            return 0
        
        session = self.session
        
        try:
            if session is None:
                async for db_session in get_db():
                    session = db_session
                    break
            
            stmt = delete(GridDataDB).where(GridDataDB.id.in_(record_ids))
            result = await session.execute(stmt)
            await session.commit()
            
            deleted_count = result.rowcount
            logger.info(f"Deleted {deleted_count} grid records")
            return deleted_count
            
        except SQLAlchemyError as e:
            if session:
                await session.rollback()
            logger.error(f"Database error deleting grid data: {e}")
            raise
        except Exception as e:
            if session:
                await session.rollback()
            logger.error(f"Unexpected error deleting grid data: {e}")
            raise