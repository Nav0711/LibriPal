from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from datetime import datetime

# Import routers
from routers import auth, books, chat, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and start background tasks"""
    print("🚀 Starting LibriPal API in development mode...")
    print("⚠️  Database connection skipped for development")
    yield
    print("🛑 Shutting down LibriPal API...")

app = FastAPI(
    title="LibriPal API",
    description="AI-Powered Library Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {
        "message": "LibriPal API is running!", 
        "status": "healthy",
        "mode": "development",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "database": "not connected (development mode)",
        "version": "1.0.0"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API is working!",
        "user": "Enthusiast-AD",
        "server_time": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)