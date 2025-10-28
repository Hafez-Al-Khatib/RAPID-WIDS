"""Test database connection and check tables"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Get DATABASE_URL from .env
db_url = os.getenv("DATABASE_URL")
print(f"DATABASE_URL: {db_url}")

# Parse connection string
# postgresql://postgres:password@localhost:5432/rapid_db
parts = db_url.replace("postgresql://", "").split("@")
user_pass = parts[0].split(":")
host_db = parts[1].split("/")

user = user_pass[0]
password = user_pass[1]
host_port = host_db[0].split(":")
host = host_port[0]
port = host_port[1]
database = host_db[1]

print(f"\nConnecting to:")
print(f"  Host: {host}")
print(f"  Port: {port}")
print(f"  Database: {database}")
print(f"  User: {user}")

try:
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    
    cursor = conn.cursor()
    
    # Check current database
    cursor.execute("SELECT current_database();")
    print(f"\n✓ Connected to database: {cursor.fetchone()[0]}")
    
    # Check PostGIS
    cursor.execute("SELECT PostGIS_Version();")
    print(f"✓ PostGIS version: {cursor.fetchone()[0]}")
    
    # Check tables
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'spatial%'
        ORDER BY tablename;
    """)
    
    tables = cursor.fetchall()
    print(f"\n✓ Tables found ({len(tables)}):")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
        count = cursor.fetchone()[0]
        print(f"    Rows: {count}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Database connection test PASSED!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
