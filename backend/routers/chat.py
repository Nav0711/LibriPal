from fastapi import APIRouter, Depends, HTTPException
from models.database import get_database
from models.pydantic_models import ChatMessage, ChatResponse, APIResponse
from services.ai_service import AIService
from services.book_service import BookService
from utils.auth import get_current_user
import json

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_assistant(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Main chat endpoint for LibriPal AI assistant"""
    ai_service = AIService()
    book_service = BookService(db)
    user_id = current_user["id"]
    
    # Store chat history
    await db.execute("""
        INSERT INTO search_history (user_id, search_query, search_type)
        VALUES ($1, $2, $3)
    """, user_id, chat_message.message, "chat")
    
    # Analyze message with AI
    ai_analysis = await ai_service.analyze_chat_message(
        chat_message.message, 
        current_user
    )
    
    intent = ai_analysis.get("intent", "help")
    extracted_info = ai_analysis.get("extracted_info", {})
    
    # Route based on detected intent
    if intent == "book_search":
        search_query = extracted_info.get("search_query", chat_message.message)
        books = await book_service.search_books_simple(search_query)
        
        return ChatResponse(
            type="book_search",
            message=f"Found {len(books)} books matching '{search_query}':",
            data=[book.__dict__ for book in books],
            suggestions=["Reserve a book", "Get recommendations", "Check due dates"]
        )
    
    elif intent == "reservation":
        book_title = extracted_info.get("book_title", "")
        if book_title:
            books = await book_service.search_books_simple(book_title, limit=3)
            return ChatResponse(
                type="book_search",
                message=f"Here are books matching '{book_title}'. Click to borrow or reserve:",
                data=[book.__dict__ for book in books]
            )
        else:
            return ChatResponse(
                type="reservation_help",
                message="Please specify which book you'd like to reserve. You can say something like 'I want to reserve Clean Code' or search for books first.",
                suggestions=["Search for books", "Show available books", "Check my reservations"]
            )
    
    elif intent == "renewal":
        borrowed_books = await book_service.get_user_borrowed_books(user_id)
        return ChatResponse(
            type="borrowed_books",
            message="Here are your currently borrowed books:",
            data=[book.__dict__ for book in borrowed_books],
            suggestions=["Renew all eligible", "Check due dates", "View fines"]
        )
    
    elif intent == "due_dates":
        borrowed_books = await book_service.get_user_borrowed_books(user_id)
        due_soon = [book for book in borrowed_books if book.urgency in ['due_soon', 'overdue']]
        
        if due_soon:
            return ChatResponse(
                type="due_dates",
                message=f"You have {len(due_soon)} books due soon or overdue:",
                data=[book.__dict__ for book in due_soon],
                suggestions=["Renew books", "Set reminders", "View all borrowed books"]
            )
        else:
            return ChatResponse(
                type="due_dates",
                message="Great! You don't have any books due soon. Here are all your borrowed books:",
                data=[book.__dict__ for book in borrowed_books],
                suggestions=["Search for more books", "Get recommendations"]
            )
    
    elif intent == "recommendations":
        recommendations = await ai_service.get_personalized_recommendations(user_id, chat_message.message)
        return ChatResponse(
            type="recommendations",
            message=ai_analysis.get("response_suggestion", "Here are some books you might like:"),
            data=[book.__dict__ for book in recommendations],
            suggestions=["Search similar books", "View reading history", "Update preferences"]
        )
    
    elif intent == "fines":
        fines = await book_service.get_user_fines(user_id)
        total_fine = sum(fine.fine_amount for fine in fines)
        
        return ChatResponse(
            type="fines",
            message=f"Your total outstanding fines: ${total_fine:.2f}",
            data=[fine.__dict__ for fine in fines],
            suggestions=["Pay fines", "View overdue books", "Set up reminders"]
        )
    
    elif intent == "library_info":
        # Get library settings
        settings = await db.fetchrow(
            "SELECT setting_value FROM library_settings WHERE setting_key = 'library_opening_hours'"
        )
        
        if settings:
            hours = json.loads(settings["setting_value"])
            return ChatResponse(
                type="library_info",
                message="Here are the library opening hours:",
                data=hours,
                suggestions=["Check library rules", "Contact library", "View location"]
            )
        else:
            return ChatResponse(
                type="library_info",
                message="Library hours: Monday-Friday 9:00 AM - 6:00 PM, Saturday 10:00 AM - 4:00 PM, Sunday: Closed",
                suggestions=["Check library rules", "Contact support"]
            )
    
    else:
        # General help
        help_message = ai_analysis.get("response_suggestion", """
Hi! I'm LibriPal, your AI library assistant. I can help you with:

📚 **Search for books**: "find books on machine learning"
📋 **Reserve books**: "I want to borrow Clean Code"  
🔄 **Renew books**: "renew my books" or "extend due dates"
📅 **Check due dates**: "when are my books due?"
💡 **Get recommendations**: "recommend books like Design Patterns"
💰 **Check fines**: "show my fines"
🕒 **Library info**: "what are the library hours?"

Just ask me naturally - I understand conversational language!
        """)
        
        return ChatResponse(
            type="help",
            message=help_message.strip(),
            suggestions=[
                "Search for books",
                "Check my borrowed books", 
                "Get book recommendations",
                "View library hours",
                "Check my fines"
            ]
        )

@router.get("/suggestions", response_model=List[str])
async def get_chat_suggestions(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get personalized chat suggestions based on user activity"""
    # Get recent search history
    recent_searches = await db.fetch("""
        SELECT search_query FROM search_history 
        WHERE user_id = $1 AND search_type = 'chat'
        ORDER BY created_at DESC LIMIT 5
    """, current_user["id"])
    
    # Get borrowed books count
    borrowed_count = await db.fetchval("""
        SELECT COUNT(*) FROM borrowed_books 
        WHERE user_id = $1 AND status = 'borrowed'
    """, current_user["id"])
    
    suggestions = [
        "Search for new books",
        "Get book recommendations",
        "Check library hours"
    ]
    
    if borrowed_count > 0:
        suggestions.insert(0, "Check my due dates")
        suggestions.insert(1, "Renew my books")
    
    return suggestions

@router.post("/feedback", response_model=APIResponse)
async def submit_chat_feedback(
    feedback_data: dict,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_database)
):
    """Submit feedback for chat responses"""
    try:
        await db.execute("""
            INSERT INTO chat_feedback (user_id, message, response_type, rating, feedback_text)
            VALUES ($1, $2, $3, $4, $5)
        """, 
        current_user["id"],
        feedback_data.get("message", ""),
        feedback_data.get("response_type", ""),
        feedback_data.get("rating", 0),
        feedback_data.get("feedback_text", "")
        )
        
        return APIResponse(
            success=True,
            message="Thank you for your feedback!"
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message="Failed to submit feedback"
        )