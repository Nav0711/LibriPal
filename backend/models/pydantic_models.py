from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import date, datetime
from decimal import Decimal

# User Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    clerk_id: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    preferences: Optional[Dict] = None

class User(UserBase):
    id: int
    clerk_id: str
    telegram_chat_id: Optional[str] = None
    preferences: Dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Book Models
class BookBase(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    description: Optional[str] = None

class BookCreate(BookBase):
    total_copies: int = 1
    available_copies: int = 1
    cover_image_url: Optional[str] = None

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    total_copies: Optional[int] = None
    available_copies: Optional[int] = None
    ai_summary: Optional[str] = None

class Book(BookBase):
    id: int
    total_copies: int
    available_copies: int
    cover_image_url: Optional[str] = None
    ai_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Search Models
class BookSearch(BaseModel):
    query: str
    limit: int = 10
    genre: Optional[str] = None
    author: Optional[str] = None
    availability_only: bool = False

class SearchResult(BaseModel):
    books: List[Book]
    total_count: int
    search_time_ms: float

# Borrowing Models
class BorrowRequest(BaseModel):
    book_id: int

class RenewalRequest(BaseModel):
    borrowed_book_id: int

class BorrowedBook(BaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: str
    book_author: str
    borrowed_date: date
    due_date: date
    returned_date: Optional[date] = None
    renewal_count: int
    fine_amount: Decimal
    status: str
    urgency: Optional[str] = None

    class Config:
        from_attributes = True

# Reservation Models
class ReservationRequest(BaseModel):
    book_id: int

class Reservation(BaseModel):
    id: int
    user_id: int
    book_id: int
    book_title: str
    reservation_date: date
    expiry_date: Optional[date] = None
    status: str
    position_in_queue: int

    class Config:
        from_attributes = True

# Chat Models
class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

class ChatResponse(BaseModel):
    type: str
    message: str
    data: Optional[List[Dict]] = None
    suggestions: Optional[List[str]] = None

# AI Models
class AIAnalysis(BaseModel):
    intent: str
    confidence: float
    extracted_info: Dict = {}
    response_suggestion: str

class BookRecommendation(BaseModel):
    book: Book
    reason: str
    confidence: float

# Notification Models
class NotificationPreferences(BaseModel):
    email_reminders: bool = True
    telegram_reminders: bool = False
    reminder_days: List[int] = [3, 1]
    recommendation_frequency: str = "weekly"

class ReminderCreate(BaseModel):
    user_id: int
    borrowed_book_id: int
    reminder_type: str
    scheduled_date: date
    channel: str = "email"

# Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

class PaginatedResponse(BaseModel):
    items: List[Dict]
    total: int
    page: int
    per_page: int
    total_pages: int

# Library Settings Models
class LibrarySettings(BaseModel):
    max_borrow_days: int = 14
    max_renewals: int = 2
    fine_per_day: Decimal = Decimal("1.00")
    max_reservations_per_user: int = 5
    library_opening_hours: Dict = {}
    reminder_days: List[int] = [3, 1]