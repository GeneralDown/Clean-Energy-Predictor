#!/usr/bin/env python3
"""
Database management CLI for Clean Energy Predictor.
"""

import asyncio
import argparse
import logging
import sys
from app.db.migrations import migration_manager
from app.db.seed_data import seed_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def migrate_up():
    """Apply all pending migrations."""
    try:
        await migration_manager.migrate_up()
        print("✅ All migrations applied successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

async def migrate_down(target_version: str = None):
    """Rollback migrations."""
    try:
        await migration_manager.migrate_down(target_version)
        print(f"✅ Migrations rolled back to {target_version or 'initial'}")
    except Exception as e:
        print(f"❌ Rollback failed: {e}")
        sys.exit(1)

async def migration_status():
    """Show migration status."""
    try:
        status = await migration_manager.get_migration_status()
        print(f"\n📊 Migration Status:")
        print(f"Total migrations: {status['total_migrations']}")
        print(f"Applied: {status['applied_migrations']}")
        print(f"Pending: {status['pending_migrations']}")
        print(f"\n📋 Migration Details:")
        
        for migration in status['migrations']:
            status_icon = "✅" if migration['applied'] else "⏳"
            print(f"{status_icon} {migration['version']}: {migration['description']}")
        
    except Exception as e:
        print(f"❌ Failed to get migration status: {e}")
        sys.exit(1)

async def seed_data(days_back: int = 7, hours_ahead: int = 24):
    """Seed database with sample data."""
    try:
        await seed_manager.seed_all(days_back, hours_ahead)
        print(f"✅ Database seeded with {days_back} days of historical data and {hours_ahead} hours of predictions")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)

async def clear_data():
    """Clear all seed data."""
    try:
        await seed_manager.clear_all_data()
        print("✅ All seed data cleared")
    except Exception as e:
        print(f"❌ Failed to clear data: {e}")
        sys.exit(1)

async def reset_database(days_back: int = 7, hours_ahead: int = 24):
    """Reset database: drop, migrate, and seed."""
    try:
        print("🔄 Resetting database...")
        await migration_manager.migrate_down()
        await migration_manager.migrate_up()
        await seed_manager.seed_all(days_back, hours_ahead)
        print("✅ Database reset complete")
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Clean Energy Predictor Database Management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Migration commands
    migrate_parser = subparsers.add_parser('migrate', help='Migration commands')
    migrate_subparsers = migrate_parser.add_subparsers(dest='migrate_action')
    
    migrate_subparsers.add_parser('up', help='Apply all pending migrations')
    
    down_parser = migrate_subparsers.add_parser('down', help='Rollback migrations')
    down_parser.add_argument('--target', help='Target version to rollback to')
    
    migrate_subparsers.add_parser('status', help='Show migration status')
    
    # Seed commands
    seed_parser = subparsers.add_parser('seed', help='Seed database with sample data')
    seed_parser.add_argument('--days-back', type=int, default=7, help='Days of historical data (default: 7)')
    seed_parser.add_argument('--hours-ahead', type=int, default=24, help='Hours of prediction data (default: 24)')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear all seed data')
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset database (drop, migrate, seed)')
    reset_parser.add_argument('--days-back', type=int, default=7, help='Days of historical data (default: 7)')
    reset_parser.add_argument('--hours-ahead', type=int, default=24, help='Hours of prediction data (default: 24)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run the appropriate command
    if args.command == 'migrate':
        if args.migrate_action == 'up':
            asyncio.run(migrate_up())
        elif args.migrate_action == 'down':
            asyncio.run(migrate_down(args.target))
        elif args.migrate_action == 'status':
            asyncio.run(migration_status())
        else:
            migrate_parser.print_help()
    
    elif args.command == 'seed':
        asyncio.run(seed_data(args.days_back, args.hours_ahead))
    
    elif args.command == 'clear':
        asyncio.run(clear_data())
    
    elif args.command == 'reset':
        asyncio.run(reset_database(args.days_back, args.hours_ahead))
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()