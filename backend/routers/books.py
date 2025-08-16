from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from models.database import get_database
from models.pydantic_models import (
    Book, BookCreate, BookUpdate, BookSearch, SearchResult,
    BorrowRequest, RenewalRequest, ReservationRequest, APIResponse
)
from services.book_service import BookService
from services.ai_service import AIService
from utils.auth import get_current_user
import time

router = APIRouter()

@router.get("/", response_model=List[Book])
async def get_books(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    genre: Optional[str] = None,
    author: Optional[str] = None,
    available_only: bool = False,
    db = Depends(get_database)
):
    """Get all books with optional filtering"""
    book_service = BookService(db)
    return await book_service.get_books(
        limit=limit,
        offset=offset,
        genre=genre,
        author=author,
        available_only=available_only
    )

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int, db = Depends(get_database)):
    """Get a specific book by ID"""
    book_service = BookService(db)
    book = await book_service.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/search", response_model=SearchResult)
async def search_books(
    search_request: BookSearch,
    db = Depends(get_database)
):
    """Search books using full-text search"""
    start_time = time.time()
    book_service = BookService(db)
    ai_service = AIService()
    
    books = await book_service.search_books(search_request)
    
    # Generate AI summaries for books that don't have them
    for book in books:
        if not book.ai_summary:
            summary = await ai_service.generate_book_summary(
                book.title, book.author, book.description or ""
            )
            book.ai_summary = summary
            await book_service.update_book_summary(book.id, summary)
    
    search_time = (time.time() - start_time) * 1000
    
    return SearchResult(
        books=books,
        total_count=len(books),
        search_time_ms=search_time
    )

@router.post("/", response_model=Book)
async def create_book(
    book_data: BookCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Create a new book (admin only)"""
    # TODO: Add admin role check
    book_service = BookService(db)
    ai_service = AIService()
    
    # Generate AI summary
    ai_summary = await ai_service.generate_book_summary(
        book_data.title, book_data.author, book_data.description or ""
    )
    
    book = await book_service.create_book(book_data, ai_summary)
    return book

@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update a book (admin only)"""
    # TODO: Add admin role check
    book_service = BookService(db)
    book = await book_service.update_book(book_id, book_data)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/borrow", response_model=APIResponse)
async def borrow_book(
    borrow_request: BorrowRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Borrow a book"""
    book_service = BookService(db)
    result = await book_service.borrow_book(current_user["id"], borrow_request.book_id)
    return result

@router.post("/renew", response_model=APIResponse)
async def renew_book(
    renewal_request: RenewalRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Renew a borrowed book"""
    book_service = BookService(db)
    result = await book_service.renew_book(current_user["id"], renewal_request.borrowed_book_id)
    return result

@router.post("/reserve", response_model=APIResponse)
async def reserve_book(
    reservation_request: ReservationRequest,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Reserve a book"""
    book_service = BookService(db)
    result = await book_service.reserve_book(current_user["id"], reservation_request.book_id)
    return result

@router.post("/{book_id}/return", response_model=APIResponse)
async def return_book(
    book_id: int,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Return a borrowed book"""
    book_service = BookService(db)
    result = await book_service.return_book(current_user["id"], book_id)
    return result

@router.get("/genres/list", response_model=List[str])
async def get_genres(db = Depends(get_database)):
    """Get all available genres"""
    genres = await db.fetch("SELECT DISTINCT genre FROM books WHERE genre IS NOT NULL ORDER BY genre")
    return [genre["genre"] for genre in genres]

@router.get("/authors/list", response_model=List[str])
async def get_authors(db = Depends(get_database)):
    """Get all authors"""
    authors = await db.fetch("SELECT DISTINCT author FROM books ORDER BY author LIMIT 100")
    return [author["author"] for author in authors]