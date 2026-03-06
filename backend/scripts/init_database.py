#!/usr/bin/env python3
"""
Simple Database Initialization Script
Creates all tables using SQLAlchemy Base.metadata.create_all()
Drops existing tables first to avoid conflicts
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models import *  # Import all models
from app.utils.logger import logger
from sqlalchemy import inspect

def init_database(drop_existing=False):
    """
    Initialize database by creating all tables
    
    Args:
        drop_existing: If True, drop all existing tables first
    """
    try:
        logger.info("Initializing database...")
        
        if drop_existing:
            # Drop all tables first to avoid conflicts
            print("⚠️  Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)
            print("✅ Existing tables dropped")
        
        # Create all tables (SQLAlchemy handles IF NOT EXISTS internally via metadata)
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully!")
        print("✅ Database tables created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize database")
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        help="Drop existing tables before creating new ones (CAUTION: deletes all data)"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (use with --drop-existing)"
    )
    args = parser.parse_args()
    
    if args.drop_existing and not args.yes:
        print("⚠️  WARNING: This will delete all existing data!")
        response = input("Continue? (y/n): ").strip().lower()
        if response not in ["y", "yes"]:
            print("Cancelled.")
            sys.exit(0)
    
    success = init_database(drop_existing=args.drop_existing)
    sys.exit(0 if success else 1)

