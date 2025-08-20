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
import asyncpg
import bcrypt
from datetime import datetime, timedelta, date
import traceback
from typing import List, Dict, Optional
import re
from decimal import Decimal
from dotenv import load_dotenv

# Conffig of  Gemini AI
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Gemini 1.5 Flash configured successfully")
else:
    model = None
    print("⚠️ Gemini API key not found")

# Database conct
DATABASE_URL = os.getenv("DATABASE_URL")

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
                return None
        return cls._connection
    
    @classmethod
    async def close_connection(cls):
        if cls._connection and not cls._connection.is_closed():
            await cls._connection.close()

# In-memory chat context storage
chat_contexts = {}

# API response cache
api_cache = {}
CACHE_DURATION = timedelta(minutes=30)

# lib const
MAX_BORROW_DAYS = 15
FINE_PER_DAY = 50  # Rupees
MAX_RENEWALS = 2
MAX_BOOKS_PER_USER = 5

class LiveBookSearchService:
    def __init__(self):
        self.open_library_url = "https://openlibrary.org/search.json"
        self.itbook_search_url = "https://api.itbook.store/1.0/search"
        self.session = None
    
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={'User-Agent': 'LibriPal/1.0 (Library Assistant Bot)'}
            )
        return self.session
    
    def is_technical_query(self, query: str) -> bool:
        technical_keywords = [
            'programming', 'coding', 'software', 'python', 'javascript', 'java',
            'react', 'node', 'algorithm', 'data structure', 'machine learning',
            'ai', 'artificial intelligence', 'web development', 'backend',
            'frontend', 'database', 'sql', 'nosql', 'devops', 'cloud'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in technical_keywords)
    
    async def search_open_library(self, query: str, limit: int = 10) -> List[Dict]:
        try:
            session = await self.get_session()
            params = {
                'q': query,
                'limit': limit,
                'fields': 'key,title,author_name,cover_i,first_publish_year,isbn,subject,publisher'
            }
            
            print(f"🔍 Searching Open Library for: {query}")
            async with session.get(self.open_library_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    books = []
                    
                    for doc in data.get('docs', []):
                        cover_url = ""
                        if doc.get('cover_i'):
                            cover_url = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                        
                        authors = doc.get('author_name', [])
                        author = authors[0] if authors else "Unknown Author"
                        
                        book = {
                            'id': doc.get('key', '').replace('/works/', ''),
                            'title': doc.get('title', 'Unknown Title'),
                            'author': author,
                            'image_url': cover_url,
                            'year': doc.get('first_publish_year', 'Unknown'),
                            'isbn': doc.get('isbn', [''])[0] if doc.get('isbn') else '',
                            'source': 'Open Library',
                            'price': '₹299'  # Default price in rupees
                        }
                        books.append(book)
                    
                    return books
                return []
        except Exception as e:
            print(f"❌ Open Library error: {e}")
            return []
    
    async def search_itbook_store(self, query: str, limit: int = 10) -> List[Dict]:
        try:
            session = await self.get_session()
            search_url = f"{self.itbook_search_url}/{query}"
            
            print(f"🔍 Searching IT Bookstore for: {query}")
            async with session.get(search_url) as response:
                if response.status == 200:
                    data = await response.json()
                    books = []
                    
                    for book_info in data.get('books', [])[:limit]:
                        price = book_info.get('price', '$0.00')
                        # Convert USD to INR (approximate)
                        if price.startswith('$'):
                            usd_price = float(price.replace('$', ''))
                            inr_price = f"₹{int(usd_price * 83)}"  # 1 USD ≈ 83 INR
                        else:
                            inr_price = '₹499'
                        
                        book = {
                            'id': book_info.get('isbn13', ''),
                            'title': book_info.get('title', 'Unknown Title'),
                            'author': book_info.get('authors', 'Unknown Author'),
                            'image_url': book_info.get('image', ''),
                            'year': book_info.get('year', 'Unknown'),
                            'isbn': book_info.get('isbn13', ''),
                            'source': 'IT Bookstore',
                            'price': inr_price
                        }
                        books.append(book)
                    
                    return books
                return []
        except Exception as e:
            print(f"❌ IT Bookstore error: {e}")
            return []
    
    async def search_books(self, query: str, limit: int = 10) -> List[Dict]:
        if not query or len(query.strip()) < 2:
            return []
        
        is_technical = self.is_technical_query(query)
        books = []
        
        if is_technical:
            itbook_results = await self.search_itbook_store(query, limit // 2 + 2)
            openlibrary_results = await self.search_open_library(query, limit // 2)
            books.extend(itbook_results)
            books.extend(openlibrary_results)
        else:
            openlibrary_results = await self.search_open_library(query, limit // 2 + 2)
            itbook_results = await self.search_itbook_store(query, limit // 2)
            books.extend(openlibrary_results)
            books.extend(itbook_results)
        
        # Remove duplicates
        unique_books = []
        seen_titles = set()
        for book in books:
            title_key = re.sub(r'[^\w\s]', '', book['title'].lower())
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_books.append(book)
        
        return unique_books[:limit]
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

book_search_service = LiveBookSearchService()

# pydantic models
class ChatMessage(BaseModel):
    message: str
    context: dict = None

class IssueBookRequest(BaseModel):
    book_id: str
    book_title: str
    book_author: str
    book_image_url: str = ""
    book_price: str = "₹299"

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting LibriPal API with Book Management...")
    await init_database()
    print("✅ LibriPal API started successfully")
    yield
    print("🛑 Shutting down LibriPal API...")
    await book_search_service.close()
    await Database.close_connection()

app = FastAPI(
    title="LibriPal API",
    description="AI-Powered Library Assistant with Complete Book Management",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def init_database():
    """Initialize database with required tables - compatible with existing schema"""
    try:
        db = await Database.get_connection()
        if db is None:
            print("⚠️ Skipping database initialization - no connection")
            return
        
        #  if users table exists and get structure
        existing_users_columns = await db.fetch("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'users' AND table_schema = 'public'
        """)
        
        users_table_exists = len(existing_users_columns) > 0
        has_clerk_id = any(col['column_name'] == 'clerk_id' for col in existing_users_columns)
        has_username = any(col['column_name'] == 'username' for col in existing_users_columns)
        
        if not users_table_exists:
            # create users tables with clerk (compatible with existing schema)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    clerk_id VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    telegram_chat_id VARCHAR(100),
                    preferences JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created users table with clerk_id")
        elif has_clerk_id:
            print("✅ Users table with clerk_id already exists")
        elif has_username and not has_clerk_id:
            # Add clerk_id column to existing username-based table
            try:
                await db.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS clerk_id VARCHAR(255)")
                await db.execute("UPDATE users SET clerk_id = username WHERE clerk_id IS NULL")
                await db.execute("ALTER TABLE users ADD CONSTRAINT users_clerk_id_unique UNIQUE (clerk_id)")
                print("✅ Added clerk_id column to existing users table")
            except Exception as e:
                print(f"⚠️ Could not add clerk_id column: {e}")
        
        # Create issued_books table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS issued_books (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                book_id VARCHAR(255) NOT NULL,
                book_title VARCHAR(500) NOT NULL,
                book_author VARCHAR(500) NOT NULL,
                book_image_url VARCHAR(500),
                book_price VARCHAR(100) DEFAULT '₹299',
                issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
                due_date DATE NOT NULL,
                return_date DATE,
                renewal_count INTEGER DEFAULT 0,
                fine_amount DECIMAL(10, 2) DEFAULT 0.00,
                status VARCHAR(50) DEFAULT 'issued',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create notifications table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                title VARCHAR(200) NOT NULL,
                message TEXT NOT NULL,
                notification_type VARCHAR(50) DEFAULT 'info',
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert or update default user (use clerk_id)
        user_exists = await db.fetchval("SELECT id FROM users WHERE clerk_id = 'enthusiast-ad-clerk-id' OR email = 'enthusiast-ad@libripal.com'")
        if not user_exists:
            user_id = await db.fetchval("""
                INSERT INTO users (clerk_id, email, first_name, last_name)
                VALUES ('enthusiast-ad-clerk-id', 'enthusiast-ad@libripal.com', 'Enthusiast', 'AD')
                RETURNING id
            """)
            print(f"✅ Created default user with ID: {user_id}")
        else:
            # Update existing user to have clerk_id if missing
            await db.execute("""
                UPDATE users 
                SET clerk_id = 'enthusiast-ad-clerk-id' 
                WHERE email = 'enthusiast-ad@libripal.com' AND clerk_id IS NULL
            """)
            print("✅ Updated existing user with clerk_id")
        
        print("✅ Database tables initialized successfully")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        traceback.print_exc()

async def get_user_id(user_identifier: str = "Enthusiast-AD") -> int:
    """Get user ID from clerk_id, username, or email"""
    try:
        db = await Database.get_connection()
        if db:
            # Try different lookup methods
            # 1. Try clerk_id first
            user_id = await db.fetchval("SELECT id FROM users WHERE clerk_id = $1", f"{user_identifier.lower()}-clerk-id")
            if user_id:
                return user_id
            
            # 2. Try email
            user_id = await db.fetchval("SELECT id FROM users WHERE email = $1", f"{user_identifier.lower()}@libripal.com")
            if user_id:
                return user_id
            
            # 3. Try username if column exists
            try:
                user_id = await db.fetchval("SELECT id FROM users WHERE username = $1", user_identifier)
                if user_id:
                    return user_id
            except:
                pass  # username column doesn't exist
            
            # 4. Try first_name
            user_id = await db.fetchval("SELECT id FROM users WHERE first_name = $1", "Enthusiast")
            if user_id:
                return user_id
            
            # 5. Get any user as fallback
            user_id = await db.fetchval("SELECT id FROM users LIMIT 1")
            if user_id:
                return user_id
        
        return 1  # Ultimate fallback
    except Exception as e:
        print(f"❌ Error getting user ID: {e}")
        return 1

async def calculate_fine(due_date: date) -> Decimal:
    """Calculate fine for overdue books"""
    today = date.today()
    if today > due_date:
        overdue_days = (today - due_date).days
        return Decimal(str(overdue_days * FINE_PER_DAY))
    return Decimal('0.00')

async def send_notification(user_id: int, title: str, message: str, notification_type: str = "info"):
    """Send notification to user"""
    try:
        db = await Database.get_connection()
        if db:
            await db.execute("""
                INSERT INTO notifications (user_id, title, message, notification_type)
                VALUES ($1, $2, $3, $4)
            """, user_id, title, message, notification_type)
            print(f"📬 Notification sent to user {user_id}: {title}")
    except Exception as e:
        print(f"❌ Error sending notification: {e}")

def get_user_context(user_id: str) -> Dict:
    if user_id not in chat_contexts:
        chat_contexts[user_id] = {
            "chat_history": [],
            "preferences": {},
            "last_interaction": datetime.utcnow(),
            "conversation_summary": "",
            "topics_discussed": [],
            "search_preferences": {"prefers_technical": False}
        }
    return chat_contexts[user_id]

def update_user_context(user_id: str, user_message: str, ai_response: str, response_type: str, search_query: str = ""):
    try:
        context = get_user_context(user_id)
        context["chat_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": user_message,
            "ai_response": ai_response[:200],
            "response_type": response_type,
            "search_query": search_query
        })
        
        if len(context["chat_history"]) > 20:
            context["chat_history"] = context["chat_history"][-20:]
        
        context["last_interaction"] = datetime.utcnow()
        
        if response_type and response_type not in context["topics_discussed"]:
            context["topics_discussed"].append(response_type)
    except Exception as e:
        print(f"Error updating user context: {e}")

async def get_user_issued_books(user_id: int) -> List[Dict]:
    """Get user's currently issued books with fine calculations"""
    try:
        db = await Database.get_connection()
        if not db:
            return []
        
        books = await db.fetch("""
            SELECT * FROM issued_books 
            WHERE user_id = $1 AND status = 'issued'
            ORDER BY due_date ASC
        """, user_id)
        
        result = []
        for book in books:
            book_dict = dict(book)
            
            # Calculate current fine
            fine = await calculate_fine(book['due_date'])
            book_dict['current_fine'] = fine
            
            # Determine urgency
            days_until_due = (book['due_date'] - date.today()).days
            if days_until_due < 0:
                book_dict['urgency'] = 'overdue'
                book_dict['urgency_text'] = f"{abs(days_until_due)} days overdue"
            elif days_until_due <= 3:
                book_dict['urgency'] = 'due_soon'
                book_dict['urgency_text'] = f"Due in {days_until_due} days"
            else:
                book_dict['urgency'] = 'normal'
                book_dict['urgency_text'] = f"Due in {days_until_due} days"
            
            # Check if renewable
            book_dict['can_renew'] = book['renewal_count'] < MAX_RENEWALS and days_until_due >= -3
            
            result.append(book_dict)
        
        return result
    except Exception as e:
        print(f"❌ Error getting issued books: {e}")
        return []

async def generate_context_aware_response(user_message: str, user_id: str = "Enthusiast-AD") -> dict:
    """Generate context-aware AI response with book management features"""
    try:
        if not model:
            return {
                "type": "error",
                "message": "AI service is not available.",
                "suggestions": ["Try again later", "Contact support"]
            }

        # take user context and issued books
        user_context = get_user_context(user_id)
        db_user_id = await get_user_id(user_id)
        issued_books = await get_user_issued_books(db_user_id)
        
        # ai context
        issued_books_summary = ""
        total_fine = Decimal('0.00')
        if issued_books:
            issued_books_summary = f"Currently issued books: {len(issued_books)}\n"
            for book in issued_books:
                total_fine += book['current_fine']
                issued_books_summary += f"- {book['book_title']} by {book['book_author']} (Due: {book['due_date']}, Fine: ₹{book['current_fine']})\n"
        
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        context_summary = ""
        if user_context["chat_history"]:
            recent_chats = user_context["chat_history"][-3:]
            context_summary = "\n".join([
                f"User: {chat['user_message']}\nAssistant: {chat['ai_response'][:80]}..."
                for chat in recent_chats
            ])
        
        prompt = f"""
You are LibriPal, an AI-powered library assistant with complete book management capabilities.

Current Date/Time: {current_time} UTC
User: {user_id}
Library Rules: Max {MAX_BORROW_DAYS} days borrowing, ₹{FINE_PER_DAY}/day fine after due date, Max {MAX_RENEWALS} renewals

USER'S CURRENT LIBRARY STATUS:
{issued_books_summary}
Total Outstanding Fines: ₹{total_fine}

RECENT CONVERSATION:
{context_summary}

CURRENT USER MESSAGE: "{user_message}"

You can help with:
1. Book search (set search_query for book searches)
2. Book issuing (set issue_book to true if user wants to issue a book)
3. Show issued books (set show_issued to true)
4. Book renewals (set show_renewals to true)
5. Fine information (set show_fines to true)
6. Library information

Respond with JSON:
{{
    "intent": "book_search|issued_books|renewals|fines|library_info|help",
    "type": "book_search|issued_books|renewals|fines|library_info|help",
    "message": "Your helpful response referencing user's current books and fines when relevant",
    "suggestions": ["suggestion1", "suggestion2", "suggestion3"],
    "search_query": "search terms if book search needed",
    "show_issued": false,
    "show_renewals": false,
    "show_fines": false
}}

Be helpful and reference their current library status when relevant!
"""

        response = await asyncio.to_thread(model.generate_content, prompt)
        
        try:
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            ai_response = json.loads(response_text)
            
            # Handleing different intents
            if ai_response.get("show_issued") or ai_response.get("intent") == "issued_books":
                ai_response["data"] = issued_books
                ai_response["type"] = "issued_books"
                ai_response["message"] += f"\n\n📚 You currently have {len(issued_books)} issued books:"
                
            elif ai_response.get("show_fines") or ai_response.get("intent") == "fines":
                fine_books = [book for book in issued_books if book['current_fine'] > 0]
                ai_response["data"] = fine_books
                ai_response["type"] = "fines"
                ai_response["message"] += f"\n\n💰 Total outstanding fines: ₹{total_fine}"
                
            elif ai_response.get("search_query"):
                search_query = ai_response["search_query"].strip()
                if search_query:
                    search_results = await book_search_service.search_books(search_query, limit=6)
                    if search_results:
                        formatted_books = []
                        for book in search_results:
                            formatted_book = {
                                "id": str(book.get("id", "")),
                                "title": str(book.get("title", "Unknown Title")),
                                "author": str(book.get("author", "Unknown Author")),
                                "image_url": str(book.get("image_url", "")),
                                "source": book.get("source", "API"),
                                "price": book.get("price", "₹299"),
                                "year": str(book.get("year", "Unknown")),
                                "isbn": book.get("isbn", ""),
                                "available_copies": 1,
                                "can_issue": len(issued_books) < MAX_BOOKS_PER_USER
                            }
                            formatted_books.append(formatted_book)
                        
                        ai_response["data"] = formatted_books
                        ai_response["type"] = "book_search"
                        ai_response["message"] += f"\n\n📚 Found {len(formatted_books)} books matching '{search_query}':"
                    else:
                        ai_response["message"] += f"\n\n❌ No books found for '{search_query}'. Try different search terms!"
            
            # Add lib info for lib_info request
            elif ai_response.get("type") == "library_info":
                ai_response["data"] = {
                    "max_borrow_days": MAX_BORROW_DAYS,
                    "fine_per_day": f"₹{FINE_PER_DAY}",
                    "max_renewals": MAX_RENEWALS,
                    "max_books": MAX_BOOKS_PER_USER,
                    "hours": {
                        "monday": "8:00 AM - 10:00 PM",
                        "tuesday": "8:00 AM - 10:00 PM",
                        "wednesday": "8:00 AM - 10:00 PM",
                        "thursday": "8:00 AM - 10:00 PM",
                        "friday": "8:00 AM - 8:00 PM",
                        "saturday": "10:00 AM - 6:00 PM",
                        "sunday": "12:00 PM - 8:00 PM"
                    }
                }
            
            # Default suggestions based on user's current status
            if not ai_response.get("suggestions"):
                suggestions = ["Search for books", "Check library hours"]
                if issued_books:
                    suggestions.insert(0, "Check my issued books")
                    if any(book['can_renew'] for book in issued_books):
                        suggestions.insert(1, "Renew my books")
                    if total_fine > 0:
                        suggestions.insert(1, "Check my fines")
                ai_response["suggestions"] = suggestions
            
            update_user_context(user_id, user_message, ai_response["message"], ai_response["type"], ai_response.get("search_query", ""))
            return ai_response
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            fallback_response = {
                "type": "help",
                "message": f"I'd be happy to help you with your library needs! You currently have {len(issued_books)} issued books with ₹{total_fine} in fines.",
                "suggestions": ["Search for books", "Check my issued books", "View library hours"]
            }
            update_user_context(user_id, user_message, fallback_response["message"], "help")
            return fallback_response
    
    except Exception as e:
        print(f"❌ Gemini AI error: {e}")
        return {
            "type": "error",
            "message": "I'm having trouble right now. Let me help you with basic library functions!",
            "suggestions": ["Search for books", "Check issued books", "Try again"]
        }

# API Endpoints

@app.post("/api/chat")
async def chat_endpoint(chat_message: ChatMessage):
    """Context-aware chat endpoint with book management"""
    try:
        user_id = "Enthusiast-AD"
        message = chat_message.message if chat_message.message else ""
        print(f"📨 Received message from {user_id}: {message}")
        
        ai_response = await generate_context_aware_response(message, user_id)
        print(f"🧠 AI Response: {ai_response.get('message', '')[:100]}...")
        
        return ai_response
    
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return {
            "type": "error",
            "message": "Sorry, I encountered an error. Please try again!",
            "suggestions": ["Try again", "Search for books", "Contact support"]
        }

@app.post("/api/books/issue")
async def issue_book(request: IssueBookRequest):
    """Issue a book to the user"""
    try:
        db_user_id = await get_user_id("Enthusiast-AD")
        db = await Database.get_connection()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Check if user has reached max books limit
        current_books = await db.fetchval(
            "SELECT COUNT(*) FROM issued_books WHERE user_id = $1 AND status = 'issued'",
            db_user_id
        )
        
        if current_books >= MAX_BOOKS_PER_USER:
            return {
                "success": False,
                "message": f"You have reached the maximum limit of {MAX_BOOKS_PER_USER} books. Please return some books first."
            }
        
        # Check if book is already issued to user
        existing = await db.fetchval(
            "SELECT id FROM issued_books WHERE user_id = $1 AND book_id = $2 AND status = 'issued'",
            db_user_id, request.book_id
        )
        
        if existing:
            return {
                "success": False,
                "message": "You have already issued this book."
            }
        
        # Issue the book
        issue_date = date.today()
        due_date = issue_date + timedelta(days=MAX_BORROW_DAYS)
        
        issue_id = await db.fetchval("""
            INSERT INTO issued_books (
                user_id, book_id, book_title, book_author, book_image_url, book_price,
                issue_date, due_date, status
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'issued')
            RETURNING id
        """, db_user_id, request.book_id, request.book_title, request.book_author,
             request.book_image_url, request.book_price, issue_date, due_date)
        
        # Send notification
        await send_notification(
            db_user_id,
            "Book Issued Successfully! 📚",
            f"'{request.book_title}' has been issued to you. Due date: {due_date.strftime('%d %B %Y')}. Return within {MAX_BORROW_DAYS} days to avoid ₹{FINE_PER_DAY}/day fine.",
            "success"
        )
        
        return {
            "success": True,
            "message": f"'{request.book_title}' issued successfully! Due date: {due_date.strftime('%d %B %Y')}",
            "data": {
                "issue_id": issue_id,
                "due_date": due_date.isoformat(),
                "fine_starts_after": due_date.isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ Book issue error: {e}")
        return {
            "success": False,
            "message": "Failed to issue book. Please try again."
        }

@app.post("/api/books/renew/{issue_id}")
async def renew_book(issue_id: int):
    """Renew an issued book"""
    try:
        db_user_id = await get_user_id("Enthusiast-AD")
        db = await Database.get_connection()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Get book details
        book = await db.fetchrow("""
            SELECT * FROM issued_books 
            WHERE id = $1 AND user_id = $2 AND status = 'issued'
        """, issue_id, db_user_id)
        
        if not book:
            return {
                "success": False,
                "message": "Book not found or already returned."
            }
        
        # Check renewal eligibility
        if book['renewal_count'] >= MAX_RENEWALS:
            return {
                "success": False,
                "message": f"Maximum {MAX_RENEWALS} renewals reached for this book."
            }
        
        # Check if book is not too overdue (max 3 days grace period)
        days_overdue = (date.today() - book['due_date']).days
        if days_overdue > 3:
            return {
                "success": False,
                "message": f"Book is {days_overdue} days overdue. Please return it to the library."
            }
        
        # Renew the book
        new_due_date = book['due_date'] + timedelta(days=MAX_BORROW_DAYS)
        new_renewal_count = book['renewal_count'] + 1
        
        await db.execute("""
            UPDATE issued_books 
            SET due_date = $1, renewal_count = $2, updated_at = CURRENT_TIMESTAMP
            WHERE id = $3
        """, new_due_date, new_renewal_count, issue_id)
        
        # Send notification
        await send_notification(
            db_user_id,
            "Book Renewed Successfully! 🔄",
            f"'{book['book_title']}' has been renewed. New due date: {new_due_date.strftime('%d %B %Y')}. Renewals used: {new_renewal_count}/{MAX_RENEWALS}",
            "success"
        )
        
        return {
            "success": True,
            "message": f"'{book['book_title']}' renewed successfully! New due date: {new_due_date.strftime('%d %B %Y')}",
            "data": {
                "new_due_date": new_due_date.isoformat(),
                "renewals_used": new_renewal_count,
                "renewals_remaining": MAX_RENEWALS - new_renewal_count
            }
        }
        
    except Exception as e:
        print(f"❌ Book renewal error: {e}")
        return {
            "success": False,
            "message": "Failed to renew book. Please try again."
        }

@app.post("/api/books/return/{issue_id}")
async def return_book(issue_id: int):
    """Return an issued book"""
    try:
        db_user_id = await get_user_id("Enthusiast-AD")
        db = await Database.get_connection()
        if not db:
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        # Get book details
        book = await db.fetchrow("""
            SELECT * FROM issued_books 
            WHERE id = $1 AND user_id = $2 AND status = 'issued'
        """, issue_id, db_user_id)
        
        if not book:
            return {
                "success": False,
                "message": "Book not found or already returned."
            }
        
        # Calculate final fine
        return_date = date.today()
        final_fine = await calculate_fine(book['due_date'])
        
        # Update book status
        await db.execute("""
            UPDATE issued_books 
            SET return_date = $1, fine_amount = $2, status = 'returned', updated_at = CURRENT_TIMESTAMP
            WHERE id = $3
        """, return_date, final_fine, issue_id)
        
        # Send notification
        if final_fine > 0:
            await send_notification(
                db_user_id,
                "Book Returned with Fine 💰",
                f"'{book['book_title']}' returned successfully. Fine: ₹{final_fine} for late return.",
                "warning"
            )
            message = f"'{book['book_title']}' returned successfully! Fine: ₹{final_fine}"
        else:
            await send_notification(
                db_user_id,
                "Book Returned Successfully! ✅",
                f"'{book['book_title']}' returned on time. Thank you!",
                "success"
            )
            message = f"'{book['book_title']}' returned successfully! No fine."
        
        return {
            "success": True,
            "message": message,
            "data": {
                "return_date": return_date.isoformat(),
                "fine_amount": float(final_fine)
            }
        }
        
    except Exception as e:
        print(f"❌ Book return error: {e}")
        return {
            "success": False,
            "message": "Failed to return book. Please try again."
        }

@app.get("/api/users/issued-books")
async def get_issued_books():
    """Get user's issued books"""
    try:
        db_user_id = await get_user_id("Enthusiast-AD")
        issued_books = await get_user_issued_books(db_user_id)
        
        return {
            "success": True,
            "issued_books": issued_books,
            "total_count": len(issued_books),
            "total_fine": sum(book['current_fine'] for book in issued_books)
        }
    except Exception as e:
        print(f"❌ Error getting issued books: {e}")
        return {
            "success": False,
            "issued_books": [],
            "total_count": 0,
            "total_fine": 0
        }

@app.get("/api/users/notifications")
async def get_notifications():
    """Get user notifications"""
    try:
        db_user_id = await get_user_id("Enthusiast-AD")
        db = await Database.get_connection()
        if not db:
            return {"notifications": []}
        
        notifications = await db.fetch("""
            SELECT * FROM notifications 
            WHERE user_id = $1 
            ORDER BY created_at DESC 
            LIMIT 20
        """, db_user_id)
        
        return {
            "notifications": [dict(n) for n in notifications],
            "unread_count": sum(1 for n in notifications if not n['is_read'])
        }
    except Exception as e:
        print(f"❌ Error getting notifications: {e}")
        return {"notifications": [], "unread_count": 0}

@app.put("/api/users/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int):
    """Mark notification as read"""
    try:
        db = await Database.get_connection()
        if db:
            await db.execute(
                "UPDATE notifications SET is_read = TRUE WHERE id = $1",
                notification_id
            )
        return {"success": True}
    except Exception as e:
        print(f"❌ Error marking notification as read: {e}")
        return {"success": False}

@app.post("/api/books/search")
async def search_books_endpoint(search_data: dict):
    """Search books using live APIs"""
    try:
        query = search_data.get("query", "")
        limit = search_data.get("limit", 10)
        
        if not query:
            return {"books": [], "total_count": 0, "error": "Invalid search query"}
        
        results = await book_search_service.search_books(query, limit)
        
        # Check user's current issued books
        db_user_id = await get_user_id("Enthusiast-AD")
        issued_books = await get_user_issued_books(db_user_id)
        
        formatted_books = []
        for book in results:
            formatted_book = {
                "id": str(book.get("id", "")),
                "title": str(book.get("title", "")),
                "author": str(book.get("author", "")),
                "image_url": str(book.get("image_url", "")),
                "price": book.get("price", "₹299"),
                "source": book.get("source", "API"),
                "year": str(book.get("year", "Unknown")),
                "available_copies": 1,
                "total_copies": 1,
                "can_issue": len(issued_books) < MAX_BOOKS_PER_USER,
                "genre": "General"
            }
            formatted_books.append(formatted_book)
        
        return {
            "books": formatted_books,
            "total_count": len(formatted_books),
            "search_time_ms": 100
        }
    except Exception as e:
        print(f"❌ Search error: {e}")
        return {"books": [], "total_count": 0, "error": str(e)}

# Existing endpoints
@app.get("/")
async def root():
    return {
        "message": "LibriPal API with Complete Book Management System!",
        "status": "healthy",
        "features": ["Book Search", "Issue/Return", "Renewals", "Fines in ₹", "Notifications"],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/users/profile")
async def get_profile():
    """Get user profile with library statistics"""
    try:
        db_user_id = await get_user_id("Enthusiast-AD")
        issued_books = await get_user_issued_books(db_user_id)
        
        total_fine = sum(book['current_fine'] for book in issued_books)
        overdue_books = [book for book in issued_books if book['urgency'] == 'overdue']
        
        return {
            "username": "Enthusiast-AD",
            "email": "enthusiast-ad@libripal.com",
            "first_name": "Enthusiast",
            "last_name": "AD",
            "member_since": "2024-01-15",
            "library_stats": {
                "books_issued": len(issued_books),
                "books_overdue": len(overdue_books),
                "total_fine": float(total_fine),
                "max_books_allowed": MAX_BOOKS_PER_USER
            },
            "preferences": {
                "email_reminders": True,
                "fine_notifications": True
            }
        }
    except Exception as e:
        print(f"❌ Profile error: {e}")
        return {"error": "Failed to load profile"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "ai_service": "gemini-1.5-flash",
        "book_apis": ["Open Library", "IT Bookstore"],
        "features": ["Issue", "Return", "Renew", "Fines", "Notifications"]
    }

if __name__ == "__main__":
    import uvicorn
    print("🤖 Starting LibriPal API with Complete Book Management...")
    print("📍 API: http://localhost:8000")
    print("🧠 AI: Gemini 1.5 Flash with Memory")
    print("📚 Features: Issue, Return, Renew, Fines (₹), Notifications")
    print("👤 User: Enthusiast-AD")
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)