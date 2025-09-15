"""
Clean Energy Predictor FastAPI Application
Main entry point for the backend API server.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import predictions, impact, locations, notifications
from app.db.migrations import migration_manager
from app.db.seed_data import seed_manager
from app.db.config import db_config
from app.db.database import close_db_connections

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Clean Energy Predictor API...")
    
    # Auto-migrate if enabled
    if db_config.auto_migrate:
        logger.info("Auto-migration enabled, applying migrations...")
        try:
            await migration_manager.migrate_up()
            logger.info("Migrations applied successfully")
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
    
    # Auto-seed if enabled
    if db_config.auto_seed:
        logger.info("Auto-seed enabled, seeding database...")
        try:
            await seed_manager.seed_all(days_back=3, hours_ahead=24)
            logger.info("Database seeded successfully")
        except Exception as e:
            logger.warning(f"Seeding failed (may already have data): {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Clean Energy Predictor API...")
    await close_db_connections()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Clean Energy Predictor API",
    description="API for predicting clean energy availability and environmental impact",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(impact.router, prefix="/api/v1", tags=["impact"])
app.include_router(locations.router, prefix="/api/v1", tags=["locations"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])

@app.get("/")
async def root():
    return {"message": "Clean Energy Predictor API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)