import asyncpg
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://libripal_user:libripal123@localhost:5432/libripal")

class Database:
    _connection: Optional[asyncpg.Connection] = None
    
    @classmethod
    async def get_connection(cls) -> asyncpg.Connection:
        if cls._connection is None or cls._connection.is_closed():
            try:
                cls._connection = await asyncpg.connect(DATABASE_URL)
                print("✅ Database connected successfully")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                print("💡 Make sure PostgreSQL is running on localhost:5432")
                if os.getenv("ENVIRONMENT") == "development":
                    print("🔧 Continuing in development mode without database...")
                    return None
                raise
        return cls._connection
    
    @classmethod
    async def close_connection(cls):
        if cls._connection and not cls._connection.is_closed():
            await cls._connection.close()

async def get_database():
    """Dependency to get database connection"""
    return await Database.get_connection()

async def create_tables():
    """Create database tables if they don't exist"""
    try:
        db = await get_database()
        if db is None:
            print("⚠️ Skipping table creation - no database connection")
            return
            
        # Basic table creation
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                clerk_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("✅ Database tables created successfully")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        if os.getenv("ENVIRONMENT") != "development":
            raise