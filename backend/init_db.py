"""
Initialize RAPID database
Creates the database and tables with PostGIS extension
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
import os

def create_database():
    """Create the rapid_db database if it doesn't exist"""
    print("Step 1: Creating database...")
    
    try:
        # Connect to PostgreSQL default database
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="root",  # Change if needed
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname='rapid_db'")
        exists = cursor.fetchone()
        
        if exists:
            print("  ✓ Database 'rapid_db' already exists")
        else:
            # Create database
            cursor.execute("CREATE DATABASE rapid_db")
            print("  ✓ Created database 'rapid_db'")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"  ✗ Error creating database: {e}")
        print("\n  Make sure PostgreSQL is running!")
        print("  Default connection: host=localhost, user=postgres, password=password")
        return False
    
    return True


def enable_postgis():
    """Enable PostGIS extension"""
    print("\nStep 2: Enabling PostGIS extension...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="root",
            database="rapid_db"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Enable PostGIS
        cursor.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        print("  ✓ PostGIS extension enabled")
        
        # Verify PostGIS version
        cursor.execute("SELECT PostGIS_Version()")
        version = cursor.fetchone()[0]
        print(f"  ✓ PostGIS version: {version}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"  ✗ Error enabling PostGIS: {e}")
        return False
    
    return True


def create_tables():
    """Create database tables using SQLAlchemy"""
    print("\nStep 3: Creating tables...")
    
    try:
        from database import init_db
        init_db()
        print("  ✓ Tables created successfully")
        
    except Exception as e:
        print(f"  ✗ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    print("="*60)
    print("RAPID Database Initialization")
    print("="*60)
    print()
    
    # Step 1: Create database
    if not create_database():
        print("\n✗ Database creation failed")
        sys.exit(1)
    
    # Step 2: Enable PostGIS
    if not enable_postgis():
        print("\n✗ PostGIS setup failed")
        sys.exit(1)
    
    # Step 3: Create tables
    if not create_tables():
        print("\n✗ Table creation failed")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ DATABASE INITIALIZED SUCCESSFULLY!")
    print("="*60)
    print()
    print("Next steps:")
    print("  1. Load sample data: python seed_data.py")
    print("  2. Start server: python main.py")
    print()


if __name__ == "__main__":
    main()
