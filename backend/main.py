from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, books, chat, users
from models.database import create_tables
import os

app = FastAPI(
    title="LibriPal API",
    description="AI-Powered Library Assistant",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and start background tasks"""
    await create_tables()

@app.get("/")
async def root():
    return {"message": "LibriPal API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-08-16T10:17:42Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)