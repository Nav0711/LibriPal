import logging
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
import asyncpg
import httpx
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class LibriPalBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.db_pool = None
        
    async def initialize_db(self):
        """Initialize database connection pool"""
        try:
            self.db_pool = await asyncpg.create_pool(DATABASE_URL)
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
    
    async def get_user_by_chat_id(self, chat_id: str):
        """Get user information by Telegram chat ID"""
        try:
            async with self.db_pool.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE telegram_chat_id = $1", 
                    str(chat_id)
                )
                return dict(user) if user else None
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    async def update_user_chat_id(self, user_id: int, chat_id: str):
        """Update user's Telegram chat ID"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET telegram_chat_id = $1 WHERE id = $2",
                    str(chat_id), user_id
                )
                return True
        except Exception as e:
            logger.error(f"Error updating chat ID: {e}")
            return False

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        welcome_message = f"""
🤖 **Welcome to LibriPal!**

Hi {user.first_name}! I'm your AI-powered library assistant.

**What I can help you with:**
📚 Search for books
📖 Check your borrowed books
📅 Get due date reminders
🔄 Renew books
💡 Get book recommendations

**Getting Started:**
1. Link your LibriPal account using `/link <your_email>`
2. Or use `/register` to create a new account

**Commands:**
/help - Show all commands
/link - Link your account
/search - Search for books
/mybooks - Show borrowed books
/profile - View your profile

Type any message to start chatting with me naturally!
        """
        
        keyboard = [
            [InlineKeyboardButton("🔗 Link Account", callback_data="link_account")],
            [InlineKeyboardButton("📖 Search Books", callback_data="search_books")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        # Store chat ID for future use
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """INSERT INTO telegram_users (chat_id, username, first_name, last_name, created_at) 
                       VALUES ($1, $2, $3, $4, $5) 
                       ON CONFLICT (chat_id) DO UPDATE SET 
                       username = EXCLUDED.username,
                       first_name = EXCLUDED.first_name,
                       last_name = EXCLUDED.last_name,
                       updated_at = CURRENT_TIMESTAMP""",
                    str(chat_id), user.username, user.first_name, user.last_name, datetime.utcnow()
                )
        except Exception as e:
            logger.error(f"Error storing telegram user: {e}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **LibriPal Bot Commands**

**Account Management:**
/start - Start the bot and get welcome message
/link <email> - Link your LibriPal account
/profile - View your profile information

**Book Management:**
/search <query> - Search for books
/mybooks - Show your currently borrowed books
/renew <book_id> - Renew a specific book
/reserve <book_id> - Reserve a book

**Information:**
/status - Check library status
/hours - Library opening hours
/help - Show this help message

**Natural Chat:**
You can also just type naturally! For example:
• "Find books about Python programming"
• "When are my books due?"
• "Recommend some science fiction books"
• "What are the library hours?"

**Settings:**
/settings - Configure notification preferences
/notifications on/off - Toggle notifications

**Support:**
If you need help, contact support@libripal.com
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /link command to link user account"""
        chat_id = update.effective_chat.id
        
        if not context.args:
            await update.message.reply_text(
                "Please provide your LibriPal email address.\n"
                "Usage: `/link your.email@example.com`",
                parse_mode='Markdown'
            )
            return
        
        email = context.args[0]
        
        # Validate email format
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            await update.message.reply_text("❌ Please provide a valid email address.")
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Find user by email
                user = await conn.fetchrow(
                    "SELECT * FROM users WHERE email = $1", email
                )
                
                if not user:
                    await update.message.reply_text(
                        f"❌ No LibriPal account found with email: {email}\n"
                        "Please make sure you've registered on the LibriPal website first."
                    )
                    return
                
                # Update user's telegram chat ID
                await conn.execute(
                    "UPDATE users SET telegram_chat_id = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2",
                    str(chat_id), user['id']
                )
                
                await update.message.reply_text(
                    f"✅ Successfully linked your account!\n"
                    f"Welcome, {user['first_name'] or 'there'}! 🎉\n\n"
                    f"You'll now receive notifications and can manage your library books through this chat."
                )
                
        except Exception as e:
            logger.error(f"Error linking account: {e}")
            await update.message.reply_text(
                "❌ Error linking account. Please try again later or contact support."
            )

    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        if not context.args:
            await update.message.reply_text(
                "Please provide a search query.\n"
                "Usage: `/search machine learning algorithms`",
                parse_mode='Markdown'
            )
            return
        
        query = ' '.join(context.args)
        await self.search_books(update, query)

    async def search_books(self, update: Update, query: str):
        """Search for books and display results"""
        chat_id = update.effective_chat.id
        
        # Check if user is linked
        user = await self.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "❌ Please link your account first using `/link <your_email>`",
                parse_mode='Markdown'
            )
            return
        
        try:
            # Send typing action
            await update.message.reply_chat_action("typing")
            
            # Search books via API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_BASE_URL}/api/books/search",
                    json={"query": query, "limit": 5},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    books = data.get("books", [])
                    
                    if not books:
                        await update.message.reply_text(
                            f"📚 No books found for: *{query}*\n\n"
                            "Try different keywords or check the spelling.",
                            parse_mode='Markdown'
                        )
                        return
                    
                    message = f"📚 Found {len(books)} books for: *{query}*\n\n"
                    
                    for i, book in enumerate(books[:5], 1):
                        availability = "✅ Available" if book.get('available_copies', 0) > 0 else "❌ Not Available"
                        
                        message += f"**{i}. {book['title']}**\n"
                        message += f"👤 Author: {book['author']}\n"
                        message += f"📊 Status: {availability}\n"
                        
                        if book.get('ai_summary'):
                            summary = book['ai_summary'][:100] + "..." if len(book['ai_summary']) > 100 else book['ai_summary']
                            message += f"📝 Summary: {summary}\n"
                        
                        message += f"🆔 ID: `{book['id']}`\n\n"
                    
                    message += "Use `/reserve <book_id>` to reserve a book!"
                    
                    await update.message.reply_text(message, parse_mode='Markdown')
                    
                else:
                    await update.message.reply_text("❌ Error searching books. Please try again later.")
                    
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            await update.message.reply_text("❌ Error searching books. Please try again later.")

    async def mybooks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mybooks command"""
        chat_id = update.effective_chat.id
        user = await self.get_user_by_chat_id(chat_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Please link your account first using `/link <your_email>`",
                parse_mode='Markdown'
            )
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                books = await conn.fetch("""
                    SELECT bb.*, b.title, b.author, b.cover_image_url,
                           CASE 
                               WHEN bb.due_date < CURRENT_DATE THEN 'overdue'
                               WHEN bb.due_date - CURRENT_DATE <= 3 THEN 'due_soon'
                               ELSE 'normal' 
                           END as urgency
                    FROM borrowed_books bb
                    JOIN books b ON bb.book_id = b.id
                    WHERE bb.user_id = $1 AND bb.status = 'borrowed'
                    ORDER BY bb.due_date
                """, user['id'])
                
                if not books:
                    await update.message.reply_text(
                        "📚 You don't have any borrowed books currently.\n"
                        "Use `/search` to find books to borrow!"
                    )
                    return
                
                message = f"📖 **Your Borrowed Books ({len(books)})**\n\n"
                
                for book in books:
                    urgency_emoji = "🚨" if book['urgency'] == 'overdue' else "⚠️" if book['urgency'] == 'due_soon' else "✅"
                    
                    message += f"{urgency_emoji} **{book['title']}**\n"
                    message += f"👤 Author: {book['author']}\n"
                    message += f"📅 Due: {book['due_date'].strftime('%B %d, %Y')}\n"
                    message += f"🔄 Renewals: {book['renewal_count']}/2\n"
                    message += f"🆔 ID: `{book['id']}`\n\n"
                
                message += "Use `/renew <book_id>` to renew a book!"
                
                # Add inline keyboard for quick actions
                keyboard = []
                for book in books[:3]:  # Show up to 3 books for quick renewal
                    if book['renewal_count'] < 2:
                        keyboard.append([
                            InlineKeyboardButton(
                                f"🔄 Renew: {book['title'][:20]}...", 
                                callback_data=f"renew_{book['id']}"
                            )
                        ])
                
                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                
                await update.message.reply_text(
                    message, 
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"Error fetching borrowed books: {e}")
            await update.message.reply_text("❌ Error fetching your books. Please try again later.")

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "link_account":
            await query.edit_message_text(
                "🔗 **Link Your Account**\n\n"
                "To link your LibriPal account, use:\n"
                "`/link your.email@example.com`\n\n"
                "Replace with your actual LibriPal email address.",
                parse_mode='Markdown'
            )
        
        elif data == "search_books":
            await query.edit_message_text(
                "📚 **Search Books**\n\n"
                "To search for books, use:\n"
                "`/search your search terms`\n\n"
                "For example:\n"
                "`/search python programming`\n"
                "`/search machine learning`",
                parse_mode='Markdown'
            )
        
        elif data == "help":
            await self.help_command(update, context)
        
        elif data.startswith("renew_"):
            book_id = data.split("_")[1]
            await self.renew_book(query, book_id)

    async def renew_book(self, query, book_id: str):
        """Renew a book"""
        chat_id = query.from_user.id
        user = await self.get_user_by_chat_id(chat_id)
        
        if not user:
            await query.edit_message_text("❌ Account not linked. Please use `/link` first.")
            return
        
        try:
            async with self.db_pool.acquire() as conn:
                # Check if book can be renewed
                book = await conn.fetchrow("""
                    SELECT bb.*, b.title 
                    FROM borrowed_books bb 
                    JOIN books b ON bb.book_id = b.id 
                    WHERE bb.id = $1 AND bb.user_id = $2 AND bb.status = 'borrowed'
                """, int(book_id), user['id'])
                
                if not book:
                    await query.edit_message_text("❌ Book not found or not borrowed by you.")
                    return
                
                if book['renewal_count'] >= 2:
                    await query.edit_message_text(
                        f"❌ Cannot renew '{book['title']}'\n"
                        "Maximum renewals (2) reached."
                    )
                    return
                
                # Check for reservations
                reservations = await conn.fetchval(
                    "SELECT COUNT(*) FROM reservations WHERE book_id = $1 AND status = 'active'",
                    book['book_id']
                )
                
                if reservations > 0:
                    await query.edit_message_text(
                        f"❌ Cannot renew '{book['title']}'\n"
                        "Book has pending reservations."
                    )
                    return
                
                # Renew the book
                from datetime import timedelta
                new_due_date = book['due_date'] + timedelta(days=14)
                
                await conn.execute("""
                    UPDATE borrowed_books 
                    SET due_date = $1, renewal_count = renewal_count + 1 
                    WHERE id = $2
                """, new_due_date, int(book_id))
                
                await query.edit_message_text(
                    f"✅ **Book Renewed Successfully!**\n\n"
                    f"📖 {book['title']}\n"
                    f"📅 New due date: {new_due_date.strftime('%B %d, %Y')}\n"
                    f"🔄 Renewals used: {book['renewal_count'] + 1}/2"
                )
                
        except Exception as e:
            logger.error(f"Error renewing book: {e}")
            await query.edit_message_text("❌ Error renewing book. Please try again later.")

    async def handle_natural_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages"""
        chat_id = update.effective_chat.id
        message_text = update.message.text.lower()
        
        # Check if user is linked
        user = await self.get_user_by_chat_id(chat_id)
        if not user:
            await update.message.reply_text(
                "👋 Hi! I'm LibriPal, your AI library assistant.\n\n"
                "To get started, please link your account:\n"
                "`/link your.email@example.com`\n\n"
                "Or use `/help` to see all available commands.",
                parse_mode='Markdown'
            )
            return
        
        # Simple intent detection
        if any(word in message_text for word in ['search', 'find', 'book', 'looking for']):
            # Extract search terms (simple approach)
            search_terms = message_text.replace('search', '').replace('find', '').replace('book', '').replace('looking for', '').strip()
            if search_terms:
                await self.search_books(update, search_terms)
            else:
                await update.message.reply_text(
                    "What books are you looking for? 📚\n"
                    "Try: 'search python programming' or 'find books about AI'"
                )
        
        elif any(word in message_text for word in ['my books', 'borrowed', 'due']):
            await self.mybooks_command(update, context)
        
        elif any(word in message_text for word in ['hours', 'open', 'time']):
            await update.message.reply_text(
                "🕒 **Library Hours**\n\n"
                "Monday - Friday: 9:00 AM - 6:00 PM\n"
                "Saturday: 10:00 AM - 4:00 PM\n"
                "Sunday: Closed\n\n"
                "For more information, visit the LibriPal website!"
            )
        
        elif any(word in message_text for word in ['help', 'commands']):
            await self.help_command(update, context)
        
        else:
            # Generic helpful response
            await update.message.reply_text(
                "🤖 I'm here to help with your library needs!\n\n"
                "I can help you:\n"
                "📚 Search for books\n"
                "📖 Check your borrowed books\n"
                "🔄 Renew books\n"
                "📅 Get due date reminders\n\n"
                "Try saying:\n"
                "• 'Search for programming books'\n"
                "• 'Show my books'\n"
                "• 'What are the library hours?'\n\n"
                "Or use `/help` for all commands!"
            )

    def setup_handlers(self):
        """Set up bot command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("link", self.link_command))
        self.application.add_handler(CommandHandler("search", self.search_command))
        self.application.add_handler(CommandHandler("mybooks", self.mybooks_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))
        
        # Message handler for natural language
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_natural_message)
        )

    async def send_reminder(self, chat_id: str, message: str):
        """Send reminder message to user"""
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
            return True
        except Exception as e:
            logger.error(f"Error sending reminder to {chat_id}: {e}")
            return False

    def run(self):
        """Run the bot"""
        try:
            # Initialize database
            asyncio.run(self.initialize_db())
            
            # Setup handlers
            self.setup_handlers()
            
            # Start the bot
            logger.info("Starting LibriPal Telegram Bot...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            if self.db_pool:
                asyncio.run(self.db_pool.close())

if __name__ == "__main__":
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is required")
        exit(1)
    
    if not DATABASE_URL:
        logger.error("DATABASE_URL environment variable is required")
        exit(1)
    
    bot = LibriPalBot()
    bot.run()