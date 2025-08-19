from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
import os
import google.generativeai as genai
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import traceback
from typing import List, Dict, Optional
import re

# Configure Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCiA6cAGyMXRUm-wx1om_IaapTiaF4grtc")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini 1.5 Flash configured successfully")
else:
    model = None
    print("⚠️ Gemini API key not found")

# In-memory chat context storage
chat_contexts = {}

# API response cache
api_cache = {}
CACHE_DURATION = timedelta(minutes=30)  # Cache for 30 minutes

class LiveBookSearchService:
    def __init__(self):
        self.open_library_url = "https://openlibrary.org/search.json"
        self.itbook_search_url = "https://api.itbook.store/1.0/search"
        self.itbook_details_url = "https://api.itbook.store/1.0/books"
        self.session = None
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={
                    'User-Agent': 'LibriPal/1.0 (Library Assistant Bot)'
                }
            )
        return self.session
    
    def is_technical_query(self, query: str) -> bool:
        """Determine if query is technical/programming related"""
        technical_keywords = [
            'programming', 'coding', 'software', 'python', 'javascript', 'java',
            'react', 'node', 'algorithm', 'data structure', 'machine learning',
            'ai', 'artificial intelligence', 'web development', 'backend',
            'frontend', 'database', 'sql', 'nosql', 'devops', 'cloud',
            'aws', 'docker', 'kubernetes', 'git', 'api', 'rest', 'graphql',
            'mobile development', 'android', 'ios', 'swift', 'kotlin',
            'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'typescript'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in technical_keywords)
    
    def get_cache_key(self, source: str, query: str, limit: int) -> str:
        """Generate cache key for API responses"""
        return f"{source}:{query.lower()}:{limit}"
    
    def is_cache_valid(self, cache_entry: dict) -> bool:
        """Check if cache entry is still valid"""
        return datetime.utcnow() - cache_entry['timestamp'] < CACHE_DURATION
    
    async def search_open_library(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Open Library API"""
        try:
            cache_key = self.get_cache_key('openlibrary', query, limit)
            
            # Check cache first
            if cache_key in api_cache and self.is_cache_valid(api_cache[cache_key]):
                print(f"📋 Using cached Open Library results for: {query}")
                return api_cache[cache_key]['data']
            
            session = await self.get_session()
            params = {
                'q': query,
                'limit': limit,
                'fields': 'key,title,author_name,cover_i,first_publish_year,isbn,subject,publisher,language,number_of_pages_median'
            }
            
            print(f"🔍 Searching Open Library for: {query}")
            async with session.get(self.open_library_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    books = []
                    
                    for doc in data.get('docs', []):
                        try:
                            # Get cover image URL
                            cover_url = ""
                            if doc.get('cover_i'):
                                cover_url = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                            
                            # Format authors
                            authors = doc.get('author_name', [])
                            author = authors[0] if authors else "Unknown Author"
                            
                            # Get ISBN
                            isbn_list = doc.get('isbn', [])
                            isbn = isbn_list[0] if isbn_list else ""
                            
                            # Get subjects/categories
                            subjects = doc.get('subject', [])
                            categories = subjects[:3] if subjects else ["General"]
                            
                            book = {
                                'id': doc.get('key', '').replace('/works/', ''),
                                'title': doc.get('title', 'Unknown Title'),
                                'author': author,
                                'image_url': cover_url,
                                'year': doc.get('first_publish_year', 'Unknown'),
                                'isbn': isbn,
                                'categories': categories,
                                'publisher': doc.get('publisher', ['Unknown'])[0] if doc.get('publisher') else 'Unknown',
                                'pages': doc.get('number_of_pages_median', 'Unknown'),
                                'source': 'Open Library',
                                'availability': 'Available',  # Simulated
                                'rating': 'Not rated',
                                'price': 'Check retailer'
                            }
                            books.append(book)
                            
                        except Exception as e:
                            print(f"Error processing Open Library book: {e}")
                            continue
                    
                    # Cache the results
                    api_cache[cache_key] = {
                        'data': books,
                        'timestamp': datetime.utcnow()
                    }
                    
                    print(f"✅ Found {len(books)} books from Open Library")
                    return books
                else:
                    print(f"❌ Open Library API error: {response.status}")
                    return []
        
        except Exception as e:
            print(f"❌ Open Library search error: {e}")
            return []
    
    async def search_itbook_store(self, query: str, limit: int = 10) -> List[Dict]:
        """Search IT Bookstore API"""
        try:
            cache_key = self.get_cache_key('itbook', query, limit)
            
            # Check cache first
            if cache_key in api_cache and self.is_cache_valid(api_cache[cache_key]):
                print(f"📋 Using cached IT Bookstore results for: {query}")
                return api_cache[cache_key]['data']
            
            session = await self.get_session()
            search_url = f"{self.itbook_search_url}/{query}"
            
            print(f"🔍 Searching IT Bookstore for: {query}")
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    books = []
                    
                    books_data = data.get('books', [])
                    for book_info in books_data[:limit]:
                        try:
                            book = {
                                'id': book_info.get('isbn13', ''),
                                'title': book_info.get('title', 'Unknown Title'),
                                'author': book_info.get('authors', 'Unknown Author'),
                                'image_url': book_info.get('image', ''),
                                'year': book_info.get('year', 'Unknown'),
                                'isbn': book_info.get('isbn13', ''),
                                'categories': ['Programming', 'Technology'],
                                'publisher': book_info.get('publisher', 'Unknown'),
                                'pages': book_info.get('pages', 'Unknown'),
                                'source': 'IT Bookstore',
                                'availability': 'Available',  # Simulated
                                'rating': book_info.get('rating', 'Not rated'),
                                'price': book_info.get('price', 'Check retailer'),
                                'description': book_info.get('desc', '')
                            }
                            books.append(book)
                            
                        except Exception as e:
                            print(f"Error processing IT Bookstore book: {e}")
                            continue
                    
                    # Cache the results
                    api_cache[cache_key] = {
                        'data': books,
                        'timestamp': datetime.utcnow()
                    }
                    
                    print(f"✅ Found {len(books)} books from IT Bookstore")
                    return books
                else:
                    print(f"❌ IT Bookstore API error: {response.status}")
                    return []
        
        except Exception as e:
            print(f"❌ IT Bookstore search error: {e}")
            return []
    
    async def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        """Search books from both APIs intelligently"""
        try:
            if not query or len(query.strip()) < 2:
                return []
            
            query = query.strip()
            is_technical = self.is_technical_query(query)
            
            books = []
            
            if is_technical:
                # For technical queries, prioritize IT Bookstore
                print(f"🤖 Technical query detected: {query}")
                itbook_results = await self.search_itbook_store(query, limit // 2 + 2)
                openlibrary_results = await self.search_open_library(query, limit // 2)
                
                # Combine results - IT Bookstore first
                books.extend(itbook_results)
                books.extend(openlibrary_results)
            else:
                # For general queries, prioritize Open Library
                print(f"📚 General query detected: {query}")
                openlibrary_results = await self.search_open_library(query, limit // 2 + 2)
                itbook_results = await self.search_itbook_store(query, limit // 2)
                
                # Combine results - Open Library first
                books.extend(openlibrary_results)
                books.extend(itbook_results)
            
            # Remove duplicates based on title similarity
            unique_books = []
            seen_titles = set()
            
            for book in books:
                title_key = re.sub(r'[^\w\s]', '', book['title'].lower())
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    unique_books.append(book)
            
            # Limit results
            final_books = unique_books[:limit]
            
            print(f"📖 Combined search found {len(final_books)} unique books")
            return final_books
        
        except Exception as e:
            print(f"❌ Combined search error: {e}")
            return []
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Initialize live book search service
book_search_service = LiveBookSearchService()

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
    print("🚀 Starting LibriPal API with Live Book Search...")
    print("📚 Open Library API: Ready")
    print("💻 IT Bookstore API: Ready")
    print("✅ LibriPal API started successfully")
    yield
    print("🛑 Shutting down LibriPal API...")
    await book_search_service.close()

app = FastAPI(
    title="LibriPal API",
    description="AI-Powered Library Assistant with Live Book Search APIs",
    version="2.0.0",
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

def get_user_context(user_id: str) -> Dict:
    """Get or create user chat context"""
    if user_id not in chat_contexts:
        chat_contexts[user_id] = {
            "chat_history": [],
            "preferences": {},
            "last_interaction": datetime.utcnow(),
            "conversation_summary": "",
            "topics_discussed": [],
            "search_preferences": {
                "prefers_technical": False,
                "favorite_categories": []
            }
        }
    return chat_contexts[user_id]

def update_user_context(user_id: str, user_message: str, ai_response: str, response_type: str, search_query: str = ""):
    """Update user context with new interaction"""
    try:
        context = get_user_context(user_id)
        
        # Add to chat history
        context["chat_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response[:200],
            "response_type": response_type,
            "search_query": search_query
        })
        
        if len(context["chat_history"]) > 20:
            context["chat_history"] = context["chat_history"][-20:]
        
        # Update preferences based on search patterns
        if search_query and book_search_service.is_technical_query(search_query):
            context["search_preferences"]["prefers_technical"] = True
        
        # Update last interaction
        context["last_interaction"] = datetime.utcnow()
        
        # Track topics discussed
        if response_type and response_type not in context["topics_discussed"]:
            context["topics_discussed"].append(response_type)
            
    except Exception as e:
        print(f"Error updating user context: {e}")

async def generate_context_aware_response(user_message: str, user_id: str = "Enthusiast-AD") -> dict:
    """Generate context-aware AI response using Gemini with live book search"""
    try:
        if not model:
            return {
                "type": "error",
                "message": "AI service is not available. Please check the configuration.",
                "suggestions": ["Try again later", "Contact support"]
            }

        if not user_message or not isinstance(user_message, str):
            return {
                "type": "error",
                "message": "Please provide a valid message.",
                "suggestions": ["Try asking about books", "Search our library", "Get help"]
            }

        # Get user context
        user_context = get_user_context(user_id)
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # Build context summary
        context_summary = ""
        if user_context["chat_history"]:
            recent_chats = user_context["chat_history"][-3:]
            context_summary = "\n".join([
                f"User: {chat['user_message']}\nAssistant: {chat['ai_response'][:80]}..."
                for chat in recent_chats
            ])
        
        topics_discussed = ", ".join(user_context["topics_discussed"]) if user_context["topics_discussed"] else "None"
        prefers_technical = user_context["search_preferences"]["prefers_technical"]
        
        prompt = f"""
You are LibriPal, an AI-powered library assistant with access to live book databases (Open Library + IT Bookstore APIs).

Current Date/Time: {current_time} UTC
User: {user_id}
User prefers technical books: {prefers_technical}

CONVERSATION CONTEXT:
Topics Previously Discussed: {topics_discussed}

RECENT CHAT HISTORY:
{context_summary}

CURRENT USER MESSAGE: "{user_message}"

Instructions:
1. If the user wants to search for books, extract search terms and set search_query
2. Remember our conversation history and build on previous interactions
3. Be conversational and reference past topics when relevant
4. For technical queries (programming, coding, software), I'll search IT Bookstore + Open Library
5. For general queries (fiction, history, etc.), I'll search Open Library + IT Bookstore
6. Always provide helpful responses about library services

Respond with JSON in this exact format:
{{
    "intent": "book_search or library_info or help or personal_chat",
    "type": "book_search or library_info or help or personal_chat", 
    "message": "Your helpful response that references our conversation history when relevant",
    "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
    "search_query": "search terms if book search needed, otherwise empty string"
}}

Be personalized, remember our conversations, and help find books from live APIs!
"""

        # Generate response with Gemini
        response = await asyncio.to_thread(model.generate_content, prompt)
        
        # Parse JSON response
        try:
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            ai_response = json.loads(response_text)
            
            # Handle book search if requested
            search_query = ai_response.get("search_query", "").strip()
            if search_query and len(search_query) > 1:
                print(f"🔍 Live API search for: {search_query}")
                search_results = await book_search_service.search_books(search_query, limit=6)
                
                if search_results:
                    # Format books for response
                    formatted_books = []
                    for book in search_results:
                        try:
                            formatted_book = {
                                "id": str(book.get("id", "")),
                                "title": str(book.get("title", "Unknown Title")),
                                "author": str(book.get("author", "Unknown Author")),
                                "image_url": str(book.get("image_url", "")),
                                "rating": str(book.get("rating", "Not rated")),
                                "reviews_count": 0,  # Not available from these APIs
                                "price": str(book.get("price", "Check retailer")),
                                "availability": str(book.get("availability", "Available")),
                                "categories": book.get("categories", []),
                                "year": str(book.get("year", "Unknown")),
                                "source": book.get("source", "API"),
                                "isbn": book.get("isbn", ""),
                                "pages": str(book.get("pages", "Unknown")),
                                "available_copies": 1,  # Simulated
                                "total_copies": 1
                            }
                            formatted_books.append(formatted_book)
                        except Exception as e:
                            print(f"Error formatting book: {e}")
                            continue
                    
                    ai_response["data"] = formatted_books
                    ai_response["type"] = "book_search"
                    
                    # Update message with search context
                    context_ref = ""
                    if user_context["chat_history"]:
                        context_ref = " (building on our previous conversation)"
                    
                    source_info = []
                    if any(book.get("source") == "IT Bookstore" for book in formatted_books):
                        source_info.append("IT Bookstore")
                    if any(book.get("source") == "Open Library" for book in formatted_books):
                        source_info.append("Open Library")
                    
                    source_text = " and ".join(source_info) if source_info else "live APIs"
                    
                    ai_response["message"] = f"{ai_response['message']}\n\n📚 Found {len(formatted_books)} books from {source_text} matching '{search_query}'{context_ref}:"
                else:
                    ai_response["message"] += f"\n\n❌ Sorry, I couldn't find any books matching '{search_query}' in the live book databases. Try different search terms!"
                
                # Update user context with search info
                update_user_context(user_id, user_message, ai_response["message"], ai_response["type"], search_query)
            
            # Add library hours for library info requests
            elif ai_response.get("type") == "library_info":
                ai_response["data"] = {
                    "monday": "8:00 AM - 10:00 PM",
                    "tuesday": "8:00 AM - 10:00 PM",
                    "wednesday": "8:00 AM - 10:00 PM",
                    "thursday": "8:00 AM - 10:00 PM",
                    "friday": "8:00 AM - 8:00 PM",
                    "saturday": "10:00 AM - 6:00 PM",
                    "sunday": "12:00 PM - 8:00 PM"
                }
                update_user_context(user_id, user_message, ai_response["message"], ai_response["type"])
            else:
                update_user_context(user_id, user_message, ai_response["message"], ai_response["type"])
            
            # Ensure suggestions exist
            if not ai_response.get("suggestions"):
                if user_context["search_preferences"]["prefers_technical"]:
                    ai_response["suggestions"] = [
                        "Find programming books",
                        "Search for algorithms",
                        "Show me web development books",
                        "What's new in tech books?"
                    ]
                else:
                    ai_response["suggestions"] = [
                        "Search for books",
                        "Find fiction books",
                        "Check library hours",
                        "Get book recommendations"
                    ]
            
            return ai_response
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw response: {response.text}")
            
            # Fallback response
            fallback_response = {
                "type": "help",
                "message": "I'd be happy to help you search for books using live APIs! I can access Open Library and IT Bookstore databases in real-time.",
                "suggestions": [
                    "Search for programming books",
                    "Find fiction books",
                    "Continue our conversation",
                    "View library hours"
                ]
            }
            
            update_user_context(user_id, user_message, fallback_response["message"], "help")
            return fallback_response
    
    except Exception as e:
        print(f"❌ Gemini AI error: {e}")
        error_response = {
            "type": "error", 
            "message": "I'm having trouble with my AI brain, but I can still search live book databases for you! Try asking for specific books.",
            "suggestions": [
                "Search for books",
                "Try again", 
                "Check library hours",
                "Get technical books"
            ]
        }
        
        update_user_context(user_id, user_message, error_response["message"], "error")
        return error_response

# Chat endpoint with context-aware Gemini AI and live book search
@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Context-aware chat endpoint with live book search APIs"""
    try:
        user_id = "Enthusiast-AD"
        message = chat_message.message if chat_message.message else ""
        print(f"📨 Received message from {user_id}: {message}")
        
        # Generate context-aware AI response with live book search
        ai_response = await generate_context_aware_response(message, user_id)
        
        print(f"🧠 Context-aware AI Response with live search: {ai_response.get('message', '')[:100]}...")
        
        return ai_response
    
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        traceback.print_exc()
        
        return {
            "type": "error",
            "message": "Sorry, I encountered an unexpected error. But I can still search live book databases for you!",
            "suggestions": [
                "Search for books",
                "Try rephrasing your question",
                "Get programming books",
                "Contact support"
            ]
        }

# Direct book search endpoint with live APIs
@app.post("/api/books/search")
async def search_books_endpoint(search_data: dict):
    """Direct book search endpoint using live APIs"""
    try:
        query = search_data.get("query", "")
        limit = search_data.get("limit", 10)
        
        if not query or not isinstance(query, str):
            return {
                "books": [],
                "total_count": 0,
                "search_time_ms": 0,
                "error": "Invalid search query"
            }
        
        print(f"🔍 Direct live API search for: {query}")
        start_time = datetime.utcnow()
        
        results = await book_search_service.search_books(query, limit)
        
        search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Format for frontend
        formatted_books = []
        for book in results:
            try:
                formatted_book = {
                    "id": str(book.get("id", "")),
                    "title": str(book.get("title", "")),
                    "author": str(book.get("author", "")),
                    "description": str(book.get("description", ""))[:200] + "..." if book.get("description") else "",
                    "image_url": str(book.get("image_url", "")),
                    "rating": str(book.get("rating", "")),
                    "available_copies": 1,  # Simulated
                    "total_copies": 1,
                    "genre": book.get("categories", [])[-1] if book.get("categories") else "General",
                    "price": book.get("price", 0),
                    "source": book.get("source", "API"),
                    "year": book.get("year", "Unknown")
                }
                formatted_books.append(formatted_book)
            except Exception as e:
                print(f"Error formatting book for search: {e}")
                continue
        
        return {
            "books": formatted_books,
            "total_count": len(formatted_books),
            "search_time_ms": int(search_time),
            "sources_used": list(set(book.get("source", "API") for book in results))
        }
    
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
        traceback.print_exc()
        return {
            "books": [],
            "total_count": 0,
            "search_time_ms": 0,
            "error": str(e)
        }

# Additional endpoints
@app.get("/")
async def root():
    return {
        "message": "LibriPal API with Live Book Search (Open Library + IT Bookstore)!",
        "status": "healthy",
        "ai_status": "enabled" if model else "disabled",
        "apis": ["Open Library", "IT Bookstore"],
        "cache_entries": len(api_cache),
        "timestamp": datetime.utcnow().isoformat(),
        "user": "Enthusiast-AD"
    }

@app.get("/api/context/{user_id}")
async def get_user_context_info(user_id: str = "Enthusiast-AD"):
    """Get user's chat context information"""
    try:
        context = get_user_context(user_id)
        return {
            "user_id": user_id,
            "total_interactions": len(context["chat_history"]),
            "topics_discussed": context["topics_discussed"],
            "last_interaction": context["last_interaction"].isoformat(),
            "has_conversation_history": len(context["chat_history"]) > 0,
            "search_preferences": context["search_preferences"],
            "recent_searches": [
                chat["search_query"] for chat in context["chat_history"][-5:] 
                if chat.get("search_query")
            ]
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ai_service": "gemini-1.5-flash" if model else "unavailable",
        "book_apis": ["Open Library", "IT Bookstore"],
        "cache_status": f"{len(api_cache)} cached queries",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/books/stats")
async def get_api_stats():
    """Get API usage statistics"""
    try:
        cache_stats = {}
        for key in api_cache:
            source = key.split(':')[0]
            cache_stats[source] = cache_stats.get(source, 0) + 1
        
        return {
            "cache_statistics": cache_stats,
            "total_cached_queries": len(api_cache),
            "available_apis": ["Open Library", "IT Bookstore"],
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/cache/clear")
async def clear_cache():
    """Clear API response cache"""
    global api_cache
    old_count = len(api_cache)
    api_cache.clear()
    return {
        "message": f"Cleared {old_count} cached queries",
        "cache_size": len(api_cache)
    }

# Other existing endpoints...
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
            "ai_recommendations": True,
            "preferred_book_sources": ["Open Library", "IT Bookstore"]
        }
    }

@app.get("/api/users/borrowed")
async def get_borrowed():
    return {"borrowed_books": []}

@app.get("/api/users/fines")
async def get_fines():
    return {"total_amount": 0.0, "fines": []}

@app.post("/api/books/borrow")
async def borrow_book(data: dict):
    return {
        "success": True,
        "message": f"Book reserved from live database! I'll remember this in our conversation."
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting LibriPal API with Live Book Search...")
    print("📍 API: http://localhost:8000")
    print("🧠 AI: Gemini 1.5 Flash with Memory")
    print("📚 Book Sources: Open Library + IT Bookstore APIs")
    print("👤 User: Enthusiast-AD")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)