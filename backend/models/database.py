import asyncpg
import os
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/libripal")

class Database:
    _connection: Optional[asyncpg.Connection] = None
    
    @classmethod
    async def get_connection(cls) -> asyncpg.Connection:
        if cls._connection is None or cls._connection.is_closed():
            cls._connection = await asyncpg.connect(DATABASE_URL)
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
    db = await get_database()
    
    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        await db.execute(schema_sql)
        print("✅ Database tables created successfully")
    else:
        print("⚠️ Schema file not found, creating basic tables...")
        
        # Basic table creation if schema file not found
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                clerk_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                telegram_chat_id VARCHAR(100),
                preferences JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                isbn VARCHAR(20) UNIQUE,
                title VARCHAR(500) NOT NULL,
                author VARCHAR(500) NOT NULL,
                publisher VARCHAR(255),
                publication_year INTEGER,
                genre VARCHAR(100),
                description TEXT,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                cover_image_url VARCHAR(500),
                ai_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS borrowed_books (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
                borrowed_date DATE NOT NULL DEFAULT CURRENT_DATE,
                due_date DATE NOT NULL,
                returned_date DATE,
                renewal_count INTEGER DEFAULT 0,
                fine_amount DECIMAL(10, 2) DEFAULT 0.00,
                status VARCHAR(50) DEFAULT 'borrowed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)