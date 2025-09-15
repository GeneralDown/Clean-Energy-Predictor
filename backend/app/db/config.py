"""
Database configuration settings for Clean Energy Predictor.
"""

import os
from typing import Optional

class DatabaseConfig:
    """Database configuration class."""
    
    def __init__(self):
        # ✅ Default to SQLite for local testing if DATABASE_URL is not set
        self.database_url = os.getenv(
            "DATABASE_URL",
            "sqlite+aiosqlite:///./test.db"
        )
        
        self.test_database_url = os.getenv(
            "TEST_DATABASE_URL", 
            "sqlite+aiosqlite:///./test_test.db"
        )
        
        # Connection pool settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "20"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "0"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "300"))  # 5 minutes
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"
        
        # Logging
        self.echo = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        
        # Migration settings
        self.auto_migrate = os.getenv("AUTO_MIGRATE", "false").lower() == "true"
        self.auto_seed = os.getenv("AUTO_SEED", "false").lower() == "true"
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite")
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL database."""
        return "postgresql" in self.database_url
    
    def get_sync_url(self) -> str:
        """Get synchronous database URL for migrations."""
        if self.is_postgresql:
            return self.database_url.replace("+asyncpg", "")
        return self.database_url

# Global configuration instance
db_config = DatabaseConfig()