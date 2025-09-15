# Database Setup Guide

This guide covers the database setup and management for the Clean Energy Predictor backend.

## Prerequisites

- PostgreSQL 12+ installed and running
- Python 3.8+ with pip
- All dependencies installed (`pip install -r requirements.txt`)

## Database Configuration

The application uses environment variables for database configuration:

```bash
# Main database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/clean_energy_predictor

# Test database
TEST_DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/clean_energy_predictor_test

# Optional configuration
DATABASE_ECHO=false          # Set to true for SQL query logging
DB_POOL_SIZE=20             # Connection pool size
DB_MAX_OVERFLOW=0           # Max overflow connections
DB_POOL_RECYCLE=300         # Connection recycle time (seconds)
DB_POOL_PRE_PING=true       # Enable connection health checks

# Auto-migration and seeding (for development)
AUTO_MIGRATE=false          # Auto-apply migrations on startup
AUTO_SEED=false             # Auto-seed database on startup
```

## Database Schema

The application includes the following tables:

### environmental_data
- Stores weather and environmental conditions
- Indexed by location and timestamp
- Includes temperature, humidity, wind speed, solar irradiance, and air quality

### grid_data
- Stores electrical grid information
- Indexed by region and timestamp
- Includes energy mix percentages and carbon intensity

### predictions
- Stores ML model predictions
- Indexed by location and target timestamp
- Includes cleanliness scores and confidence levels

### notification_subscriptions
- Stores user notification preferences
- Indexed by email and location
- Supports email, SMS, and push notifications

### notification_logs
- Tracks notification delivery history
- Indexed by subscription and timestamp

## Database Management

Use the `manage_db.py` script for database operations:

### Migration Commands

```bash
# Check migration status
python manage_db.py migrate status

# Apply all pending migrations
python manage_db.py migrate up

# Rollback migrations
python manage_db.py migrate down
python manage_db.py migrate down --target 001  # Rollback to specific version
```

### Data Management Commands

```bash
# Seed database with sample data
python manage_db.py seed
python manage_db.py seed --days-back 14 --hours-ahead 48

# Clear all seed data
python manage_db.py clear

# Reset database (drop, migrate, seed)
python manage_db.py reset
python manage_db.py reset --days-back 7 --hours-ahead 24
```

## Development Setup

1. **Create databases:**
   ```sql
   CREATE DATABASE clean_energy_predictor;
   CREATE DATABASE clean_energy_predictor_test;
   ```

2. **Set environment variables:**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/clean_energy_predictor"
   export TEST_DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/clean_energy_predictor_test"
   ```

3. **Initialize database:**
   ```bash
   python manage_db.py migrate up
   python manage_db.py seed
   ```

4. **Run tests:**
   ```bash
   pytest tests/test_database.py -v
   ```

## Production Setup

1. **Set production environment variables**
2. **Run migrations:**
   ```bash
   python manage_db.py migrate up
   ```
3. **Do NOT use auto-seed in production**
4. **Monitor database performance and connection pools**

## Performance Considerations

- All tables include appropriate indexes for common query patterns
- Connection pooling is configured for optimal performance
- Timestamps use timezone-aware datetime fields
- Constraints ensure data integrity
- Concurrent index creation minimizes downtime

## Backup and Recovery

For production deployments:

1. **Regular backups:**
   ```bash
   pg_dump clean_energy_predictor > backup_$(date +%Y%m%d_%H%M%S).sql
   ```

2. **Point-in-time recovery setup**
3. **Monitor disk space and connection limits**
4. **Regular maintenance (VACUUM, ANALYZE)**

## Troubleshooting

### Common Issues

1. **Connection errors:**
   - Check PostgreSQL is running
   - Verify connection string format
   - Check firewall/network settings

2. **Migration failures:**
   - Check database permissions
   - Review migration logs
   - Ensure no conflicting schema changes

3. **Performance issues:**
   - Monitor connection pool usage
   - Check for missing indexes
   - Analyze slow query logs

### Useful Commands

```bash
# Check database connection
python -c "from app.db.database import engine; import asyncio; asyncio.run(engine.connect())"

# View migration status
python manage_db.py migrate status

# Check table sizes
psql -d clean_energy_predictor -c "SELECT schemaname,tablename,pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname='public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"
```