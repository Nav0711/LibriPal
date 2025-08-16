from typing import List, Optional, Dict
import asyncpg
from datetime import date, timedelta
from models.pydantic_models import (
    Book, BookCreate, BookUpdate, BookSearch, BorrowedBook,
    Reservation, APIResponse
)
from decimal import Decimal

class BookService:
    def __init__(self, db: asyncpg.Connection):
        self.db = db
    
    async def get_books(
        self, 
        limit: int = 20, 
        offset: int = 0,
        genre: Optional[str] = None,
        author: Optional[str] = None,
        available_only: bool = False
    ) -> List[Book]:
        """Get books with optional filtering"""
        
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        param_count = 1
        
        if genre:
            query += f" AND genre ILIKE ${param_count}"
            params.append(f"%{genre}%")
            param_count += 1
        
        if author:
            query += f" AND author ILIKE ${param_count}"
            params.append(f"%{author}%")
            param_count += 1
        
        if available_only:
            query += f" AND available_copies > 0"
        
        query += f" ORDER BY title LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])
        
        books = await self.db.fetch(query, *params)
        return [Book(**dict(book)) for book in books]
    
    async def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Get a specific book by ID"""
        book = await self.db.fetchrow("SELECT * FROM books WHERE id = $1", book_id)
        return Book(**dict(book)) if book else None
    
    async def search_books(self, search_request: BookSearch) -> List[Book]:
        """Search books using full-text search"""
        query = """
            SELECT *, 
                   ts_rank(to_tsvector('english', title || ' ' || author || ' ' || COALESCE(description, '')), 
                           plainto_tsquery('english', $1)) as rank
            FROM books 
            WHERE to_tsvector('english', title || ' ' || author || ' ' || COALESCE(description, '')) 
                  @@ plainto_tsquery('english', $1)
        """
        
        params = [search_request.query]
        param_count = 2
        
        if search_request.genre:
            query += f" AND genre ILIKE ${param_count}"
            params.append(f"%{search_request.genre}%")
            param_count += 1
        
        if search_request.author:
            query += f" AND author ILIKE ${param_count}"
            params.append(f"%{search_request.author}%")
            param_count += 1
        
        if search_request.availability_only:
            query += " AND available_copies > 0"
        
        query += f" ORDER BY rank DESC, title LIMIT ${param_count}"
        params.append(search_request.limit)
        
        books = await self.db.fetch(query, *params)
        return [Book(**dict(book)) for book in books]
    
    async def search_books_simple(self, query: str, limit: int = 10) -> List[Book]:
        """Simple book search for chat interface"""
        books = await self.db.fetch("""
            SELECT * FROM books 
            WHERE title ILIKE $1 OR author ILIKE $1 OR description ILIKE $1
            ORDER BY 
                CASE 
                    WHEN title ILIKE $1 THEN 1
                    WHEN author ILIKE $1 THEN 2
                    ELSE 3
                END,
                title
            LIMIT $2
        """, f"%{query}%", limit)
        
        return [Book(**dict(book)) for book in books]
    
    async def create_book(self, book_data: BookCreate, ai_summary: str = "") -> Book:
        """Create a new book"""
        book_id = await self.db.fetchval("""
            INSERT INTO books (
                title, author, isbn, publisher, publication_year, genre, 
                description, total_copies, available_copies, cover_image_url, ai_summary
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id
        """, 
        book_data.title, book_data.author, book_data.isbn, book_data.publisher,
        book_data.publication_year, book_data.genre, book_data.description,
        book_data.total_copies, book_data.available_copies, book_data.cover_image_url,
        ai_summary)
        
        return await self.get_book_by_id(book_id)
    
    async def update_book(self, book_id: int, book_data: BookUpdate) -> Optional[Book]:
        """Update a book"""
        # Build dynamic update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in book_data.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                values.append(value)
                param_count += 1
        
        if not update_fields:
            return await self.get_book_by_id(book_id)
        
        query = f"UPDATE books SET {', '.join(update_fields)} WHERE id = ${param_count}"
        values.append(book_id)
        
        await self.db.execute(query, *values)
        return await self.get_book_by_id(book_id)
    
    async def update_book_summary(self, book_id: int, summary: str):
        """Update book's AI summary"""
        await self.db.execute(
            "UPDATE books SET ai_summary = $1 WHERE id = $2",
            summary, book_id
        )
    
    async def borrow_book(self, user_id: int, book_id: int) -> APIResponse:
        """Borrow a book or add to reservation queue"""
        # Check if book exists and is available
        book = await self.db.fetchrow(
            "SELECT * FROM books WHERE id = $1", book_id
        )
        
        if not book:
            return APIResponse(
                success=False,
                message="Book not found"
            )
        
        # Check if user already has this book
        existing_borrow = await self.db.fetchrow("""
            SELECT id FROM borrowed_books 
            WHERE user_id = $1 AND book_id = $2 AND status = 'borrowed'
        """, user_id, book_id)
        
        if existing_borrow:
            return APIResponse(
                success=False,
                message="You already have this book borrowed"
            )
        
        if book["available_copies"] > 0:
            # Book is available - create borrowing record
            max_borrow_days = await self.db.fetchval(
                "SELECT setting_value::int FROM library_settings WHERE setting_key = 'max_borrow_days'"
            ) or 14
            
            due_date = date.today() + timedelta(days=max_borrow_days)
            
            borrowed_id = await self.db.fetchval("""
                INSERT INTO borrowed_books (user_id, book_id, due_date) 
                VALUES ($1, $2, $3) RETURNING id
            """, user_id, book_id, due_date)
            
            # Update available copies
            await self.db.execute(
                "UPDATE books SET available_copies = available_copies - 1 WHERE id = $1",
                book_id
            )
            
            return APIResponse(
                success=True,
                message=f"Book borrowed successfully! Due date: {due_date.strftime('%B %d, %Y')}",
                data={"borrowed_id": borrowed_id, "due_date": due_date.isoformat()}
            )
        else:
            # Book not available - add to reservation queue
            queue_position = await self.db.fetchval(
                "SELECT COUNT(*) + 1 FROM reservations WHERE book_id = $1 AND status = 'active'",
                book_id
            )
            
            reservation_id = await self.db.fetchval("""
                INSERT INTO reservations (user_id, book_id, position_in_queue, expiry_date) 
                VALUES ($1, $2, $3, $4) RETURNING id
            """, user_id, book_id, queue_position, date.today() + timedelta(days=7))
            
            return APIResponse(
                success=True,
                message=f"Book reserved! You are #{queue_position} in the queue.",
                data={"reservation_id": reservation_id, "queue_position": queue_position}
            )
    
    async def renew_book(self, user_id: int, borrowed_book_id: int) -> APIResponse:
        """Renew a borrowed book"""
        # Get borrowed book details
        borrowed_book = await self.db.fetchrow("""
            SELECT bb.*, b.title 
            FROM borrowed_books bb 
            JOIN books b ON bb.book_id = b.id 
            WHERE bb.id = $1 AND bb.user_id = $2 AND bb.status = 'borrowed'
        """, borrowed_book_id, user_id)
        
        if not borrowed_book:
            return APIResponse(
                success=False,
                message="Borrowed book not found"
            )
        
        # Check renewal limits
        max_renewals = await self.db.fetchval(
            "SELECT setting_value::int FROM library_settings WHERE setting_key = 'max_renewals'"
        ) or 2
        
        if borrowed_book["renewal_count"] >= max_renewals:
            return APIResponse(
                success=False,
                message=f"Maximum renewals ({max_renewals}) reached for this book"
            )
        
        # Check if there are pending reservations
        pending_reservations = await self.db.fetchval(
            "SELECT COUNT(*) FROM reservations WHERE book_id = $1 AND status = 'active'",
            borrowed_book["book_id"]
        )
        
        if pending_reservations > 0:
            return APIResponse(
                success=False,
                message="Cannot renew - book has pending reservations"
            )
        
        # Renew the book
        max_borrow_days = await self.db.fetchval(
            "SELECT setting_value::int FROM library_settings WHERE setting_key = 'max_borrow_days'"
        ) or 14
        
        new_due_date = borrowed_book["due_date"] + timedelta(days=max_borrow_days)
        
        await self.db.execute("""
            UPDATE borrowed_books 
            SET due_date = $1, renewal_count = renewal_count + 1 
            WHERE id = $2
        """, new_due_date, borrowed_book_id)
        
        return APIResponse(
            success=True,
            message=f"'{borrowed_book['title']}' renewed until {new_due_date.strftime('%B %d, %Y')}",
            data={"new_due_date": new_due_date.isoformat()}
        )
    
    async def reserve_book(self, user_id: int, book_id: int) -> APIResponse:
        """Reserve a book (same as borrow for unavailable books)"""
        return await self.borrow_book(user_id, book_id)
    
    async def return_book(self, user_id: int, book_id: int) -> APIResponse:
        """Return a borrowed book"""
        # Find the borrowed book record
        borrowed_book = await self.db.fetchrow("""
            SELECT bb.*, b.title 
            FROM borrowed_books bb 
            JOIN books b ON bb.book_id = b.id 
            WHERE bb.user_id = $1 AND bb.book_id = $2 AND bb.status = 'borrowed'
        """, user_id, book_id)
        
        if not borrowed_book:
            return APIResponse(
                success=False,
                message="No active borrowing record found for this book"
            )
        
        # Calculate fine if overdue
        fine_amount = Decimal("0.00")
        if borrowed_book["due_date"] < date.today():
            days_overdue = (date.today() - borrowed_book["due_date"]).days
            fine_per_day = await self.db.fetchval(
                "SELECT setting_value::decimal FROM library_settings WHERE setting_key = 'fine_per_day'"
            ) or Decimal("1.00")
            fine_amount = days_overdue * fine_per_day
        
        # Update borrowed book record
        await self.db.execute("""
            UPDATE borrowed_books 
            SET returned_date = CURRENT_DATE, status = 'returned', fine_amount = $1
            WHERE id = $2
        """, fine_amount, borrowed_book["id"])
        
        # Update available copies
        await self.db.execute(
            "UPDATE books SET available_copies = available_copies + 1 WHERE id = $1",
            book_id
        )
        
        # Check for pending reservations
        next_reservation = await self.db.fetchrow("""
            SELECT r.*, u.email, u.first_name 
            FROM reservations r
            JOIN users u ON r.user_id = u.id
            WHERE r.book_id = $1 AND r.status = 'active'
            ORDER BY r.position_in_queue
            LIMIT 1
        """, book_id)
        
        message = f"'{borrowed_book['title']}' returned successfully!"
        if fine_amount > 0:
            message += f" Fine assessed: ${fine_amount}"
        
        # TODO: Send notification to next person in queue
        
        return APIResponse(
            success=True,
            message=message,
            data={"fine_amount": float(fine_amount)}
        )
    
    async def get_user_borrowed_books(self, user_id: int) -> List[BorrowedBook]:
        """Get user's currently borrowed books"""
        books = await self.db.fetch("""
            SELECT bb.*, b.title as book_title, b.author as book_author, b.cover_image_url,
                   CASE 
                       WHEN bb.due_date < CURRENT_DATE THEN 'overdue'
                       WHEN bb.due_date - CURRENT_DATE <= 3 THEN 'due_soon'
                       ELSE 'normal' 
                   END as urgency
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.id
            WHERE bb.user_id = $1 AND bb.status = 'borrowed'
            ORDER BY bb.due_date
        """, user_id)
        
        return [BorrowedBook(**dict(book)) for book in books]
    
    async def get_user_fines(self, user_id: int) -> List[BorrowedBook]:
        """Get user's books with outstanding fines"""
        fines = await self.db.fetch("""
            SELECT bb.*, b.title as book_title, b.author as book_author, b.cover_image_url
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.id
            WHERE bb.user_id = $1 AND bb.fine_amount > 0
            ORDER BY bb.due_date
        """, user_id)
        
        return [BorrowedBook(**dict(fine)) for fine in fines]