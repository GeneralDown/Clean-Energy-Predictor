"""
Database migration utilities for Clean Energy Predictor.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import engine, Base, AsyncSessionLocal

logger = logging.getLogger(__name__)

class Migration:
    """Base class for database migrations."""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.utcnow()
    
    async def up(self, session: AsyncSession) -> None:
        """Apply the migration."""
        raise NotImplementedError("Subclasses must implement up() method")
    
    async def down(self, session: AsyncSession) -> None:
        """Rollback the migration."""
        raise NotImplementedError("Subclasses must implement down() method")

class CreateMigrationTableMigration(Migration):
    """Create the migrations tracking table."""
    
    def __init__(self):
        super().__init__("001", "Create migrations table")
    
    async def up(self, session: AsyncSession) -> None:
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) NOT NULL UNIQUE,
                description VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await session.commit()
        logger.info("Created migrations table")
    
    async def down(self, session: AsyncSession) -> None:
        await session.execute(text("DROP TABLE IF EXISTS migrations"))
        await session.commit()
        logger.info("Dropped migrations table")

class CreateInitialSchemaMigration(Migration):
    """Create the initial database schema."""
    
    def __init__(self):
        super().__init__("002", "Create initial schema")
    
    async def up(self, session: AsyncSession) -> None:
        # Create all tables using SQLAlchemy models
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created initial database schema")
    
    async def down(self, session: AsyncSession) -> None:
        # Drop all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Dropped all database tables")

class AddIndexesMigration(Migration):
    """Add performance indexes."""
    
    def __init__(self):
        super().__init__("003", "Add performance indexes")
    
    async def up(self, session: AsyncSession) -> None:
        # Additional indexes for better query performance
        indexes = [
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_env_location_timestamp_score ON environmental_data (location, timestamp) WHERE temperature IS NOT NULL",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_grid_region_renewable ON grid_data (region, renewable_percentage) WHERE renewable_percentage IS NOT NULL",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pred_location_score ON predictions (location, cleanliness_score) WHERE cleanliness_score >= 70",
        ]
        
        for index_sql in indexes:
            try:
                await session.execute(text(index_sql))
                await session.commit()
            except Exception as e:
                logger.warning(f"Index creation failed (may already exist): {e}")
                await session.rollback()
        
        logger.info("Added performance indexes")
    
    async def down(self, session: AsyncSession) -> None:
        indexes_to_drop = [
            "DROP INDEX IF EXISTS idx_env_location_timestamp_score",
            "DROP INDEX IF EXISTS idx_grid_region_renewable", 
            "DROP INDEX IF EXISTS idx_pred_location_score",
        ]
        
        for drop_sql in indexes_to_drop:
            await session.execute(text(drop_sql))
        
        await session.commit()
        logger.info("Dropped performance indexes")

class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self):
        self.migrations: List[Migration] = [
            CreateMigrationTableMigration(),
            CreateInitialSchemaMigration(),
            AddIndexesMigration(),
        ]
    
    async def get_applied_migrations(self, session: AsyncSession) -> List[str]:
        """Get list of applied migration versions."""
        try:
            result = await session.execute(text("SELECT version FROM migrations ORDER BY version"))
            return [row[0] for row in result.fetchall()]
        except Exception:
            # Migrations table doesn't exist yet
            return []
    
    async def apply_migration(self, migration: Migration, session: AsyncSession) -> None:
        """Apply a single migration."""
        try:
            logger.info(f"Applying migration {migration.version}: {migration.description}")
            await migration.up(session)
            
            # Record the migration
            await session.execute(text(
                "INSERT INTO migrations (version, description) VALUES (:version, :description)"
            ), {"version": migration.version, "description": migration.description})
            await session.commit()
            
            logger.info(f"Successfully applied migration {migration.version}")
        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            await session.rollback()
            raise
    
    async def rollback_migration(self, migration: Migration, session: AsyncSession) -> None:
        """Rollback a single migration."""
        try:
            logger.info(f"Rolling back migration {migration.version}: {migration.description}")
            await migration.down(session)
            
            # Remove the migration record
            await session.execute(text(
                "DELETE FROM migrations WHERE version = :version"
            ), {"version": migration.version})
            await session.commit()
            
            logger.info(f"Successfully rolled back migration {migration.version}")
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration.version}: {e}")
            await session.rollback()
            raise
    
    async def migrate_up(self) -> None:
        """Apply all pending migrations."""
        async with AsyncSessionLocal() as session:
            applied_migrations = await self.get_applied_migrations(session)
            
            for migration in self.migrations:
                if migration.version not in applied_migrations:
                    await self.apply_migration(migration, session)
            
            logger.info("All migrations applied successfully")
    
    async def migrate_down(self, target_version: str = None) -> None:
        """Rollback migrations to target version."""
        async with AsyncSessionLocal() as session:
            applied_migrations = await self.get_applied_migrations(session)
            
            # Rollback migrations in reverse order
            for migration in reversed(self.migrations):
                if migration.version in applied_migrations:
                    if target_version and migration.version <= target_version:
                        break
                    await self.rollback_migration(migration, session)
            
            logger.info(f"Rolled back migrations to version {target_version or 'initial'}")
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        async with AsyncSessionLocal() as session:
            applied_migrations = await self.get_applied_migrations(session)
            
            status = {
                "total_migrations": len(self.migrations),
                "applied_migrations": len(applied_migrations),
                "pending_migrations": len(self.migrations) - len(applied_migrations),
                "migrations": []
            }
            
            for migration in self.migrations:
                status["migrations"].append({
                    "version": migration.version,
                    "description": migration.description,
                    "applied": migration.version in applied_migrations
                })
            
            return status

# Global migration manager instance
migration_manager = MigrationManager()