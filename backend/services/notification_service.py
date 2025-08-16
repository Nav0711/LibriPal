import smtplib
import asyncio
import httpx
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import date, datetime
from models.database import get_database

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@libripal.com")
    
    async def send_email(self, to_email: str, subject: str, body: str, html_body: str = None) -> bool:
        """Send email notification"""
        try:
            if not self.smtp_username or not self.smtp_password:
                print("Email credentials not configured")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def send_telegram_message(self, chat_id: str, message: str, parse_mode: str = "HTML") -> bool:
        """Send Telegram message"""
        try:
            if not self.telegram_bot_token:
                print("Telegram bot token not configured")
                return False
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": parse_mode
                })
                
                return response.status_code == 200
                
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
            return False
    
    async def send_due_date_reminder(self, user: Dict, book: Dict, days_until_due: int):
        """Send due date reminder notification"""
        if days_until_due == 0:
            subject = f"📚 Book Due Today: {book['title']}"
            urgency = "today"
        elif days_until_due < 0:
            subject = f"🚨 Overdue Book: {book['title']}"
            urgency = f"{abs(days_until_due)} days overdue"
        else:
            subject = f"⏰ Book Due in {days_until_due} Days: {book['title']}"
            urgency = f"in {days_until_due} days"
        
        # Email content
        email_body = f"""
Hi {user['first_name'] or 'there'},

This is a friendly reminder that your borrowed book is due {urgency}.

Book Details:
📖 Title: {book['title']}
✍️ Author: {book['author']}
📅 Due Date: {book['due_date']}

To avoid any late fees, please return the book on time or renew it if eligible.

You can manage your books through LibriPal:
• Chat with our AI assistant
• Check your borrowed books
• Renew eligible books

Thank you for using LibriPal!

Best regards,
The LibriPal Team
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #3b82f6;">📚 LibriPal Reminder</h2>
                
                <p>Hi {user['first_name'] or 'there'},</p>
                
                <p>This is a friendly reminder that your borrowed book is due <strong>{urgency}</strong>.</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e293b;">Book Details</h3>
                    <p><strong>📖 Title:</strong> {book['title']}</p>
                    <p><strong>✍️ Author:</strong> {book['author']}</p>
                    <p><strong>📅 Due Date:</strong> {book['due_date']}</p>
                </div>
                
                <p>To avoid any late fees, please return the book on time or renew it if eligible.</p>
                
                <div style="background-color: #eff6ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <h4 style="margin-top: 0;">You can manage your books through LibriPal:</h4>
                    <ul>
                        <li>Chat with our AI assistant</li>
                        <li>Check your borrowed books</li>
                        <li>Renew eligible books</li>
                    </ul>
                </div>
                
                <p>Thank you for using LibriPal!</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The LibriPal Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        # Telegram message
        telegram_message = f"""
📚 <b>LibriPal Reminder</b>

Hi {user['first_name'] or 'there'}! Your book is due {urgency}.

📖 <b>{book['title']}</b>
✍️ by {book['author']}
📅 Due: {book['due_date']}

Please return or renew your book to avoid late fees.

💬 Chat with LibriPal to manage your books!
        """
        
        # Send notifications based on user preferences
        preferences = user.get('preferences', {})
        sent_email = False
        sent_telegram = False
        
        if preferences.get('email_reminders', True):
            sent_email = await self.send_email(user['email'], subject, email_body, html_body)
        
        if preferences.get('telegram_reminders', False) and user.get('telegram_chat_id'):
            sent_telegram = await self.send_telegram_message(user['telegram_chat_id'], telegram_message)
        
        # Log the reminder
        db = await get_database()
        await db.execute("""
            INSERT INTO reminders (user_id, borrowed_book_id, reminder_type, scheduled_date, sent_at, status, channel)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """, 
        user['id'], book['borrowed_book_id'], f"{days_until_due}_day", 
        date.today(), datetime.utcnow(), 
        'sent' if (sent_email or sent_telegram) else 'failed',
        'both' if (sent_email and sent_telegram) else ('email' if sent_email else 'telegram' if sent_telegram else 'none')
        )
        
        return sent_email or sent_telegram
    
    async def send_reservation_notification(self, user: Dict, book: Dict):
        """Send notification when reserved book becomes available"""
        subject = f"📚 Your Reserved Book is Available: {book['title']}"
        
        email_body = f"""
Great news, {user['first_name'] or 'there'}!

Your reserved book is now available for pickup:

📖 Title: {book['title']}
✍️ Author: {book['author']}

Please visit the library within the next 24 hours to collect your book. 
If you don't collect it within this time, it will be offered to the next person in the queue.

You can also manage your reservations through LibriPal.

Happy reading!

Best regards,
The LibriPal Team
        """
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #10b981;">📚 Great News!</h2>
                
                <p>Hi {user['first_name'] or 'there'},</p>
                
                <p>Your reserved book is now <strong>available for pickup</strong>!</p>
                
                <div style="background-color: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981;">
                    <h3 style="margin-top: 0; color: #1e293b;">Available Book</h3>
                    <p><strong>📖 Title:</strong> {book['title']}</p>
                    <p><strong>✍️ Author:</strong> {book['author']}</p>
                </div>
                
                <div style="background-color: #fef3c7; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>⏰ Important:</strong> Please visit the library within the next <strong>24 hours</strong> to collect your book. If you don't collect it within this time, it will be offered to the next person in the queue.</p>
                </div>
                
                <p>You can also manage your reservations through LibriPal.</p>
                
                <p>Happy reading!</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>The LibriPal Team</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        telegram_message = f"""
🎉 <b>Great News!</b>

Hi {user['first_name'] or 'there']}! Your reserved book is now available.

📖 <b>{book['title']}</b>
✍️ by {book['author']}

⏰ Please collect within 24 hours or it will be offered to the next person.

📍 Visit the library to pick up your book!
        """
        
        # Send notifications
        preferences = user.get('preferences', {})
        
        if preferences.get('email_reminders', True):
            await self.send_email(user['email'], subject, email_body, html_body)
        
        if preferences.get('telegram_reminders', False) and user.get('telegram_chat_id'):
            await self.send_telegram_message(user['telegram_chat_id'], telegram_message)
    
    async def send_welcome_notification(self, user: Dict):
        """Send welcome email to new users"""
        subject = "Welcome to LibriPal! 📚"
        
        email_body = f"""
Welcome to LibriPal, {user['first_name'] or 'there'}!

We're excited to have you join our community of readers. LibriPal is your AI-powered library assistant that makes managing your library experience effortless.

Here's what you can do with LibriPal:

🔍 Smart Search: Find books using natural language
💬 AI Chat: Get instant help and recommendations
📅 Due Date Tracking: Never miss a return date
🔄 Easy Renewals: Extend your borrowing period
⏰ Smart Reminders: Get notified via email and Telegram
💡 Personalized Recommendations: Discover books you'll love

Get started by:
1. Searching for your first book
2. Setting up your notification preferences
3. Chatting with our AI assistant

Happy reading!

Best regards,
The LibriPal Team
        """
        
        await self.send_email(user['email'], subject, email_body)
    
    async def send_fine_notification(self, user: Dict, total_fine: float, overdue_books: List[Dict]):
        """Send notification about outstanding fines"""
        subject = f"📋 Outstanding Library Fines: ${total_fine:.2f}"
        
        books_list = "\n".join([f"• {book['title']} - ${book['fine_amount']:.2f}" for book in overdue_books])
        
        email_body = f"""
Hi {user['first_name'] or 'there'},

You have outstanding library fines that need your attention.

Total Amount Due: ${total_fine:.2f}

Books with fines:
{books_list}

Please settle these fines at your earliest convenience. You can:
• Visit the library to pay in person
• Use our online payment system
• Contact us for payment assistance

Thank you for your prompt attention to this matter.

Best regards,
The LibriPal Team
        """
        
        await self.send_email(user['email'], subject, email_body)