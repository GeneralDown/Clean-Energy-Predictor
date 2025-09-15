"""
Database configuration and connection management for Clean Energy Predictor.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import logging
from .config import db_config

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    db_config.database_url,
    echo=db_config.echo,
    pool_size=db_config.pool_size,
    max_overflow=db_config.max_overflow,
    pool_pre_ping=db_config.pool_pre_ping,
    pool_recycle=db_config.pool_recycle,
)

# Create test engine
test_engine = create_async_engine(
    db_config.test_database_url,
    echo=False,
    poolclass=NullPool,  # No pooling for tests
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create test session factory
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get test database session.
    """
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Test database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """
    Create all tables in the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

async def drop_tables():
    """
    Drop all tables in the database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Database tables dropped successfully")

async def create_test_tables():
    """
    Create all tables in the test database.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Test database tables created successfully")

async def drop_test_tables():
    """
    Drop all tables in the test database.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("Test database tables dropped successfully")

async def close_db_connections():
    """
    Close all database connections.
    """
    await engine.dispose()
    await test_engine.dispose()
    logger.info("Database connections closed")