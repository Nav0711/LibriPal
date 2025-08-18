#!/usr/bin/env python3
"""
Database setup script for LibriPal
This script creates the database, runs migrations, and seeds initial data.
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://libripal_user:password@localhost:5432/libripal")

async def create_database():
    """Create the database if it doesn't exist"""
    # Parse the database URL to get connection info
    from urllib.parse import urlparse
    
    parsed = urlparse(DATABASE_URL)
    db_name = parsed.path[1:]  # Remove leading slash
    
    # Connect to postgres database to create the target database
    postgres_url = DATABASE_URL.replace(f"/{db_name}", "/postgres")
    
    try:
        conn = await asyncpg.connect(postgres_url)
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")
        else:
            print(f"ℹ️ Database '{db_name}' already exists")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

async def run_sql_file(conn, file_path):
    """Run SQL commands from a file"""
    try:
        with open(file_path, 'r') as f:
            sql_content = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                await conn.execute(statement)
        
        print(f"✅ Executed {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error executing {file_path}: {e}")
        return False

async def setup_database():
    """Set up the complete database"""
    print("🚀 Starting LibriPal database setup...")
    
    # Create database
    if not await create_database():
        return False
    
    # Connect to the target database
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Get the project root directory
        project_root = Path(__file__).parent.parent
        
        # Run schema
        schema_file = project_root / "database" / "schema.sql"
        if schema_file.exists():
            await run_sql_file(conn, schema_file)
        else:
            # Fallback to backend schema
            backend_schema = project_root / "backend" / "database" / "schema.sql"
            if backend_schema.exists():
                await run_sql_file(conn, backend_schema)
        
        # Run migrations
        migrations_dir = project_root / "database" / "migrations"
        if migrations_dir.exists():
            migration_files = sorted(migrations_dir.glob("*.sql"))
            for migration_file in migration_files:
                await run_sql_file(conn, migration_file)
        
        # Run seeds
        seeds_dir = project_root / "database" / "seeds"
        if seeds_dir.exists():
            seed_files = sorted(seeds_dir.glob("*.sql"))
            for seed_file in seed_files:
                await run_sql_file(conn, seed_file)
        
        await conn.close()
        print("✅ Database setup completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

async def reset_database():
    """Reset the database (drop and recreate)"""
    from urllib.parse import urlparse
    
    parsed = urlparse(DATABASE_URL)
    db_name = parsed.path[1:]
    postgres_url = DATABASE_URL.replace(f"/{db_name}", "/postgres")
    
    try:
        conn = await asyncpg.connect(postgres_url)
        
        # Terminate all connections to the database
        await conn.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = '{db_name}' AND pid <> pg_backend_pid()
        """)
        
        # Drop database
        await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
        print(f"🗑️ Database '{db_name}' dropped")
        
        await conn.close()
        
        # Recreate database
        return await setup_database()
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        return False

async def check_database_status():
    """Check database status and show table information"""
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Get table list
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        print(f"📊 Database Status:")
        print(f"Tables: {len(tables)}")
        
        for table in tables:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table['table_name']}")
            print(f"  - {table['table_name']}: {count} rows")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error checking database status: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LibriPal Database Setup")
    parser.add_argument(
        "action", 
        choices=["setup", "reset", "status"],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    if args.action == "setup":
        success = asyncio.run(setup_database())
    elif args.action == "reset":
        confirm = input("⚠️ This will delete all data. Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            success = asyncio.run(reset_database())
        else:
            print("❌ Reset cancelled")
            return
    elif args.action == "status":
        success = asyncio.run(check_database_status())
    
    if success:
        print("🎉 Operation completed successfully!")
    else:
        print("💥 Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()