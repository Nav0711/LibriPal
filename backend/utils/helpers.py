from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import hashlib

def calculate_due_date(borrow_date: date = None, max_days: int = 14) -> date:
    """Calculate due date for a borrowed book"""
    if borrow_date is None:
        borrow_date = date.today()
    return borrow_date + timedelta(days=max_days)

def calculate_fine(due_date: date, return_date: date = None, fine_per_day: float = 1.0) -> float:
    """Calculate fine for overdue book"""
    if return_date is None:
        return_date = date.today()
    
    if return_date <= due_date:
        return 0.0
    
    days_overdue = (return_date - due_date).days
    return days_overdue * fine_per_day

def format_urgency(due_date: date) -> str:
    """Determine urgency level based on due date"""
    today = date.today()
    days_until_due = (due_date - today).days
    
    if days_until_due < 0:
        return "overdue"
    elif days_until_due <= 3:
        return "due_soon"
    else:
        return "normal"

def clean_search_query(query: str) -> str:
    """Clean and normalize search query"""
    # Remove special characters and extra spaces
    cleaned = re.sub(r'[^\w\s]', ' ', query)
    cleaned = ' '.join(cleaned.split())
    return cleaned.strip().lower()

def generate_isbn_checksum(isbn: str) -> str:
    """Generate ISBN-13 checksum (simplified)"""
    # Remove any non-digit characters
    digits = ''.join(filter(str.isdigit, isbn))
    
    if len(digits) != 12:
        return isbn  # Return original if not proper length
    
    # Calculate checksum
    total = 0
    for i, digit in enumerate(digits):
        weight = 1 if i % 2 == 0 else 3
        total += int(digit) * weight
    
    checksum = (10 - (total % 10)) % 10
    return digits + str(checksum)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def hash_password(password: str) -> str:
    """Hash password (placeholder - use proper hashing in production)"""
    return hashlib.sha256(password.encode()).hexdigest()

def paginate_results(items: List[Any], page: int = 1, per_page: int = 20) -> Dict:
    """Paginate a list of items"""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    
    paginated_items = items[start:end]
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

def format_date_for_display(date_obj: date) -> str:
    """Format date for user-friendly display"""
    if date_obj == date.today():
        return "Today"
    elif date_obj == date.today() + timedelta(days=1):
        return "Tomorrow"
    elif date_obj == date.today() - timedelta(days=1):
        return "Yesterday"
    else:
        return date_obj.strftime("%B %d, %Y")

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text for search indexing"""
    # Simple keyword extraction (in production, use NLP libraries)
    words = clean_search_query(text).split()
    
    # Filter out common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'within'
    }
    
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Return unique keywords, limited to max_keywords
    return list(dict.fromkeys(keywords))[:max_keywords]

def calculate_reading_level(text: str) -> str:
    """Estimate reading level of text (simplified)"""
    if not text:
        return "Unknown"
    
    words = text.split()
    sentences = text.split('.')
    
    if len(sentences) == 0 or len(words) == 0:
        return "Unknown"
    
    avg_words_per_sentence = len(words) / len(sentences)
    avg_syllables_per_word = sum(count_syllables(word) for word in words) / len(words)
    
    # Simplified Flesch Reading Ease calculation
    flesch_score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
    
    if flesch_score >= 90:
        return "Elementary"
    elif flesch_score >= 80:
        return "Middle School"
    elif flesch_score >= 70:
        return "High School"
    elif flesch_score >= 60:
        return "College"
    else:
        return "Graduate"

def count_syllables(word: str) -> int:
    """Count syllables in a word (simplified)"""
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    prev_was_vowel = False
    
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            count += 1
        prev_was_vowel = is_vowel
    
    # Handle edge cases
    if word.endswith('e'):
        count -= 1
    if count == 0:
        count = 1
    
    return count

def generate_book_slug(title: str, author: str) -> str:
    """Generate URL-friendly slug for a book"""
    combined = f"{title} {author}".lower()
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', combined)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def get_book_cover_placeholder(title: str) -> str:
    """Generate a placeholder cover URL based on book title"""
    # Simple placeholder service (you could use a real service like Unsplash)
    encoded_title = title.replace(' ', '+')
    return f"https://via.placeholder.com/300x450/3b82f6/ffffff?text={encoded_title}"

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount for display"""
    if currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def get_time_ago(dt: datetime) -> str:
    """Get human-readable time difference"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "Just now"

class LibraryConstants:
    """Constants used throughout the library system"""
    
    # Book statuses
    BOOK_STATUS_AVAILABLE = "available"
    BOOK_STATUS_BORROWED = "borrowed"
    BOOK_STATUS_RESERVED = "reserved"
    BOOK_STATUS_MAINTENANCE = "maintenance"
    
    # Borrowing statuses
    BORROW_STATUS_ACTIVE = "borrowed"
    BORROW_STATUS_RETURNED = "returned"
    BORROW_STATUS_OVERDUE = "overdue"
    BORROW_STATUS_LOST = "lost"
    
    # Reservation statuses
    RESERVATION_STATUS_ACTIVE = "active"
    RESERVATION_STATUS_FULFILLED = "fulfilled"
    RESERVATION_STATUS_EXPIRED = "expired"
    RESERVATION_STATUS_CANCELLED = "cancelled"
    
    # Reminder types
    REMINDER_TYPE_3_DAY = "3_day"
    REMINDER_TYPE_1_DAY = "1_day"
    REMINDER_TYPE_OVERDUE = "overdue"
    REMINDER_TYPE_RESERVATION = "reservation_available"
    
    # Notification channels
    CHANNEL_EMAIL = "email"
    CHANNEL_TELEGRAM = "telegram"
    CHANNEL_BOTH = "both"
    
    # Default settings
    DEFAULT_BORROW_DAYS = 14
    DEFAULT_MAX_RENEWALS = 2
    DEFAULT_FINE_PER_DAY = 1.00
    DEFAULT_MAX_RESERVATIONS = 5