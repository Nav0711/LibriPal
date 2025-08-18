from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import google.generativeai as genai
import asyncio
import json
from datetime import datetime
import traceback

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCiA6cAGyMXRUm-wx1om_IaapTiaF4grtc")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini AI configured successfully")
else:
    model = None
    print("⚠️ Gemini API key not found")

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    context: dict = None

class ChatResponse(BaseModel):
    type: str
    message: str
    data: list = None
    suggestions: list = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application"""
    print("🚀 Starting LibriPal API with Gemini AI...")
    print("✅ LibriPal API started successfully")
    yield
    print("🛑 Shutting down LibriPal API...")

app = FastAPI(
    title="LibriPal API",
    description="AI-Powered Library Assistant with Gemini AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

async def generate_gemini_response(user_message: str, user_context: dict = None) -> dict:
    """Generate AI response using Gemini"""
    try:
        if not model:
            return {
                "type": "error",
                "message": "AI service is not available. Please check the configuration.",
                "suggestions": ["Try again later", "Contact support"]
            }

        # Create context-aware prompt
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""
You are LibriPal, an AI-powered library assistant. You are helpful, friendly, and knowledgeable about library services.

Current Date/Time: {current_time} UTC
User: Enthusiast-AD

User message: "{user_message}"

Analyze the user's message and respond helpfully. Determine the intent and provide appropriate responses.

Possible intents and how to handle them:
- book_search: User wants to find books
- borrowed_books: User wants to check borrowed books
- due_dates: User wants to check due dates
- renewals: User wants to renew books
- recommendations: User wants book recommendations
- library_info: User wants library information (hours, policies, etc.)
- fines: User wants to check fines
- help: General help or unclear intent

Respond with JSON in this exact format:
{{
    "intent": "detected_intent",
    "type": "response_type",
    "message": "Your helpful response to the user",
    "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
    "data": []
}}

Guidelines:
- Be conversational and helpful
- If asking about books, suggest popular academic/programming books
- Include 3-5 practical suggestions
- Keep responses concise but informative
- For library hours, mention standard academic library hours
- Be encouraging and supportive

Remember: You are LibriPal, helping students and researchers with their library needs.
"""

        # Generate response with Gemini
        response = await asyncio.to_thread(model.generate_content, prompt)
        
        # Parse JSON response
        try:
            # Clean the response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            ai_response = json.loads(response_text)
            
            # Add sample data for book searches
            if ai_response.get("intent") == "book_search" or ai_response.get("type") == "book_search":
                ai_response["data"] = [
                    {
                        "id": 1,
                        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
                        "author": "Robert C. Martin",
                        "description": "A comprehensive guide to writing clean, maintainable code",
                        "available_copies": 3,
                        "total_copies": 5,
                        "genre": "Programming"
                    },
                    {
                        "id": 2,
                        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
                        "author": "Gang of Four",
                        "description": "Classic book on software design patterns",
                        "available_copies": 2,
                        "total_copies": 4,
                        "genre": "Programming"
                    },
                    {
                        "id": 3,
                        "title": "Introduction to Algorithms",
                        "author": "Thomas H. Cormen",
                        "description": "Comprehensive introduction to algorithms and data structures",
                        "available_copies": 1,
                        "total_copies": 3,
                        "genre": "Computer Science"
                    }
                ]
            
            # Add sample data for library info
            elif ai_response.get("intent") == "library_info" or ai_response.get("type") == "library_info":
                ai_response["data"] = {
                    "monday": "8:00 AM - 10:00 PM",
                    "tuesday": "8:00 AM - 10:00 PM",
                    "wednesday": "8:00 AM - 10:00 PM",
                    "thursday": "8:00 AM - 10:00 PM",
                    "friday": "8:00 AM - 8:00 PM",
                    "saturday": "10:00 AM - 6:00 PM",
                    "sunday": "12:00 PM - 8:00 PM"
                }
            
            return ai_response
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response.text}")
            
            # Fallback response if JSON parsing fails
            return {
                "type": "help",
                "message": response.text if response.text else "I'd be happy to help you with your library needs! You can ask me about searching for books, checking due dates, renewing books, or getting recommendations.",
                "suggestions": [
                    "Search for books",
                    "Check my borrowed books",
                    "Get book recommendations",
                    "View library hours"
                ]
            }
    
    except Exception as e:
        print(f"❌ Gemini AI error: {e}")
        return {
            "type": "error", 
            "message": "I'm having trouble connecting to my AI brain right now. Let me help you with some basic library functions!",
            "suggestions": [
                "Search for books",
                "Check library hours",
                "Get help with renewals",
                "Contact library staff"
            ]
        }

# Chat endpoint with Gemini AI
@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Main chat endpoint powered by Gemini AI"""
    try:
        print(f"📨 Received message from Enthusiast-AD: {chat_message.message}")
        
        # Generate AI response
        ai_response = await generate_gemini_response(
            chat_message.message, 
            chat_message.context
        )
        
        print(f"🤖 AI Response: {ai_response.get('message', '')[:100]}...")
        
        return ai_response
    
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        traceback.print_exc()
        
        return {
            "type": "error",
            "message": "Sorry, I encountered an unexpected error. Please try asking your question again.",
            "suggestions": [
                "Try rephrasing your question",
                "Ask about library hours",
                "Search for books",
                "Contact support"
            ]
        }

# Other endpoints
@app.get("/")
async def root():
    return {
        "message": "LibriPal API with Gemini AI is running!",
        "status": "healthy",
        "ai_status": "enabled" if model else "disabled",
        "timestamp": datetime.utcnow().isoformat(),
        "user": "Enthusiast-AD"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_service": "gemini-pro" if model else "unavailable",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/test")
async def test_gemini():
    """Test Gemini AI connectivity"""
    if not model:
        return {"status": "error", "message": "Gemini AI not configured"}
    
    try:
        test_response = await asyncio.to_thread(
            model.generate_content, 
            "Respond with 'Gemini AI is working correctly for LibriPal!' if you can see this message."
        )
        return {
            "status": "success",
            "message": "Gemini AI is connected",
            "test_response": test_response.text
        }
    except Exception as e:
        return {"status": "error", "message": f"Gemini AI test failed: {str(e)}"}

# User endpoints (mock data for development)
@app.get("/api/users/profile")
async def get_profile():
    return {
        "username": "Enthusiast-AD",
        "email": "enthusiast-ad@libripal.com",
        "first_name": "Enthusiast",
        "last_name": "AD",
        "member_since": "2024-01-15",
        "preferences": {
            "email_reminders": True,
            "ai_recommendations": True
        }
    }

@app.get("/api/users/borrowed")
async def get_borrowed():
    return {
        "borrowed_books": [
            {
                "id": 1,
                "title": "Python Machine Learning",
                "author": "Sebastian Raschka",
                "due_date": "2025-08-25",
                "renewal_count": 0,
                "urgency": "normal"
            }
        ]
    }

@app.get("/api/users/fines")
async def get_fines():
    return {"total_amount": 0.0, "fines": []}

@app.post("/api/books/search")
async def search_books(search_data: dict):
    query = search_data.get("query", "")
    
    # Mock search results
    books = [
        {
            "id": 1,
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "description": "A handbook of agile software craftsmanship",
            "available_copies": 3,
            "total_copies": 5,
            "genre": "Programming",
            "ai_summary": "Essential reading for software developers who want to write maintainable, readable code."
        },
        {
            "id": 2,
            "title": "Design Patterns",
            "author": "Gang of Four",
            "description": "Elements of reusable object-oriented software",
            "available_copies": 2,
            "total_copies": 4,
            "genre": "Programming",
            "ai_summary": "Classic reference for understanding common software design patterns and their applications."
        }
    ]
    
    # Filter books based on query
    if query:
        books = [book for book in books if query.lower() in book["title"].lower() or query.lower() in book["author"].lower()]
    
    return {
        "books": books,
        "total_count": len(books),
        "search_time_ms": 45
    }

@app.post("/api/books/borrow")
async def borrow_book(data: dict):
    return {
        "success": True,
        "message": f"Book with ID {data.get('book_id')} has been borrowed successfully! Due date: August 25, 2025."
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting LibriPal API with Gemini AI...")
    print("📍 API: http://localhost:8000")
    print("🧠 AI: Gemini Pro")
    print("👤 User: Enthusiast-AD")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)