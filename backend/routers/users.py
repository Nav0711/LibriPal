from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.database import get_database
from models.pydantic_models import (
    User, UserUpdate, BorrowedBook, Reservation, 
    NotificationPreferences, APIResponse
)
from services.book_service import BookService
from utils.auth import get_current_user
import json

router = APIRouter()

@router.get("/profile", response_model=User)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=APIResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update user profile"""
    try:
        # Build update query dynamically
        update_fields = []
        values = []
        param_count = 1
        
        if user_data.first_name is not None:
            update_fields.append(f"first_name = ${param_count}")
            values.append(user_data.first_name)
            param_count += 1
            
        if user_data.last_name is not None:
            update_fields.append(f"last_name = ${param_count}")
            values.append(user_data.last_name)
            param_count += 1
            
        if user_data.telegram_chat_id is not None:
            update_fields.append(f"telegram_chat_id = ${param_count}")
            values.append(user_data.telegram_chat_id)
            param_count += 1
            
        if user_data.preferences is not None:
            update_fields.append(f"preferences = ${param_count}")
            values.append(json.dumps(user_data.preferences))
            param_count += 1
        
        if update_fields:
            update_fields.append(f"updated_at = ${param_count}")
            values.append("CURRENT_TIMESTAMP")
            values.append(current_user["id"])
            
            query = f"""
                UPDATE users 
                SET {', '.join(update_fields)}
                WHERE id = ${param_count + 1}
            """
            
            await db.execute(query, *values[:-1], current_user["id"])
        
        return APIResponse(
            success=True,
            message="Profile updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@router.get("/borrowed", response_model=List[BorrowedBook])
async def get_user_borrowed_books(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's borrowed books"""
    book_service = BookService(db)
    return await book_service.get_user_borrowed_books(current_user["id"])

@router.get("/reservations", response_model=List[Reservation])
async def get_user_reservations(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's active reservations"""
    reservations = await db.fetch("""
        SELECT r.*, b.title as book_title
        FROM reservations r
        JOIN books b ON r.book_id = b.id
        WHERE r.user_id = $1 AND r.status = 'active'
        ORDER BY r.position_in_queue
    """, current_user["id"])
    
    return [dict(reservation) for reservation in reservations]

@router.get("/fines", response_model=dict)
async def get_user_fines(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's outstanding fines"""
    book_service = BookService(db)
    fines = await book_service.get_user_fines(current_user["id"])
    total_amount = sum(fine.fine_amount for fine in fines)
    
    return {
        "fines": [fine.__dict__ for fine in fines],
        "total_amount": float(total_amount),
        "currency": "USD"
    }

@router.get("/reading-history", response_model=List[dict])
async def get_reading_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    db = Depends(get_database)
):
    """Get user's reading history"""
    history = await db.fetch("""
        SELECT bb.*, b.title, b.author, b.genre, b.cover_image_url
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.id
        WHERE bb.user_id = $1
        ORDER BY bb.borrowed_date DESC
        LIMIT $2
    """, current_user["id"], limit)
    
    return [dict(record) for record in history]

@router.get("/statistics", response_model=dict)
async def get_user_statistics(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get user's reading statistics"""
    stats = {}
    
    # Total books borrowed
    stats["total_borrowed"] = await db.fetchval("""
        SELECT COUNT(*) FROM borrowed_books WHERE user_id = $1
    """, current_user["id"])
    
    # Books currently borrowed
    stats["currently_borrowed"] = await db.fetchval("""
        SELECT COUNT(*) FROM borrowed_books 
        WHERE user_id = $1 AND status = 'borrowed'
    """, current_user["id"])
    
    # Total fines
    stats["total_fines"] = await db.fetchval("""
        SELECT COALESCE(SUM(fine_amount), 0) FROM borrowed_books 
        WHERE user_id = $1 AND fine_amount > 0
    """, current_user["id"])
    
    # Favorite genres
    favorite_genres = await db.fetch("""
        SELECT b.genre, COUNT(*) as count
        FROM borrowed_books bb
        JOIN books b ON bb.book_id = b.id
        WHERE bb.user_id = $1 AND b.genre IS NOT NULL
        GROUP BY b.genre
        ORDER BY count DESC
        LIMIT 5
    """, current_user["id"])
    
    stats["favorite_genres"] = [
        {"genre": row["genre"], "count": row["count"]} 
        for row in favorite_genres
    ]
    
    # Reading streak (days with activity)
    stats["reading_streak"] = await db.fetchval("""
        SELECT COUNT(DISTINCT DATE(borrowed_date))
        FROM borrowed_books 
        WHERE user_id = $1 AND borrowed_date >= CURRENT_DATE - INTERVAL '30 days'
    """, current_user["id"])
    
    return stats

@router.get("/notifications/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(
    current_user: dict = Depends(get_current_user)
):
    """Get user's notification preferences"""
    prefs = current_user.get("preferences", {})
    return NotificationPreferences(**prefs)

@router.put("/notifications/preferences", response_model=APIResponse)
async def update_notification_preferences(
    preferences: NotificationPreferences,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update user's notification preferences"""
    try:
        current_prefs = current_user.get("preferences", {})
        current_prefs.update(preferences.dict())
        
        await db.execute("""
            UPDATE users 
            SET preferences = $1, updated_at = CURRENT_TIMESTAMP
            WHERE id = $2
        """, json.dumps(current_prefs), current_user["id"])
        
        return APIResponse(
            success=True,
            message="Notification preferences updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to update preferences: {str(e)}"
        )

@router.post("/export-data", response_model=APIResponse)
async def export_user_data(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Export all user data (GDPR compliance)"""
    try:
        # Collect all user data
        user_data = {
            "profile": current_user,
            "borrowed_books": [],
            "reservations": [],
            "search_history": [],
            "fines": []
        }
        
        # Get borrowed books
        borrowed = await db.fetch("""
            SELECT bb.*, b.title, b.author 
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.id
            WHERE bb.user_id = $1
        """, current_user["id"])
        user_data["borrowed_books"] = [dict(book) for book in borrowed]
        
        # Get reservations
        reservations = await db.fetch("""
            SELECT r.*, b.title 
            FROM reservations r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = $1
        """, current_user["id"])
        user_data["reservations"] = [dict(res) for res in reservations]
        
        # Get search history
        history = await db.fetch("""
            SELECT * FROM search_history WHERE user_id = $1
        """, current_user["id"])
        user_data["search_history"] = [dict(search) for search in history]
        
        # TODO: Generate downloadable file and send via email
        
        return APIResponse(
            success=True,
            message="Data export requested. You will receive an email with your data shortly."
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export data: {str(e)}"
        )