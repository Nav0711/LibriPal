import asyncio
from datetime import date, timedelta
from typing import List, Dict
from models.database import get_database
from services.notification_service import NotificationService

class ReminderService:
    def __init__(self):
        self.notification_service = NotificationService()
    
    async def process_due_date_reminders(self):
        """Process and send due date reminders"""
        db = await get_database()
        
        try:
            # Get reminder settings
            reminder_days = await db.fetchval(
                "SELECT setting_value FROM library_settings WHERE setting_key = 'reminder_days'"
            )
            reminder_days = eval(reminder_days) if reminder_days else [3, 1]
            
            for days_before in reminder_days:
                target_date = date.today() + timedelta(days=days_before)
                
                # Get books due on target date that haven't been reminded
                books_due = await db.fetch("""
                    SELECT bb.*, b.title, b.author, u.id as user_id, u.email, u.first_name, 
                           u.telegram_chat_id, u.preferences
                    FROM borrowed_books bb
                    JOIN books b ON bb.book_id = b.id
                    JOIN users u ON bb.user_id = u.id
                    WHERE bb.due_date = $1 
                    AND bb.status = 'borrowed'
                    AND NOT EXISTS (
                        SELECT 1 FROM reminders r 
                        WHERE r.borrowed_book_id = bb.id 
                        AND r.reminder_type = $2
                        AND r.status = 'sent'
                    )
                """, target_date, f"{days_before}_day")
                
                for book in books_due:
                    user = {
                        'id': book['user_id'],
                        'email': book['email'],
                        'first_name': book['first_name'],
                        'telegram_chat_id': book['telegram_chat_id'],
                        'preferences': book['preferences'] or {}
                    }
                    
                    book_info = {
                        'borrowed_book_id': book['id'],
                        'title': book['title'],
                        'author': book['author'],
                        'due_date': book['due_date'].strftime('%B %d, %Y')
                    }
                    
                    await self.notification_service.send_due_date_reminder(
                        user, book_info, days_before
                    )
                    
                    # Small delay to avoid overwhelming email servers
                    await asyncio.sleep(0.1)
            
            # Check for overdue books
            await self.process_overdue_reminders()
            
        except Exception as e:
            print(f"Error processing due date reminders: {e}")
        finally:
            await db.close()
    
    async def process_overdue_reminders(self):
        """Process reminders for overdue books"""
        db = await get_database()
        
        try:
            # Get overdue books that haven't been reminded today
            overdue_books = await db.fetch("""
                SELECT bb.*, b.title, b.author, u.id as user_id, u.email, u.first_name,
                       u.telegram_chat_id, u.preferences,
                       (CURRENT_DATE - bb.due_date) as days_overdue
                FROM borrowed_books bb
                JOIN books b ON bb.book_id = b.id
                JOIN users u ON bb.user_id = u.id
                WHERE bb.due_date < CURRENT_DATE 
                AND bb.status = 'borrowed'
                AND NOT EXISTS (
                    SELECT 1 FROM reminders r 
                    WHERE r.borrowed_book_id = bb.id 
                    AND r.reminder_type = 'overdue'
                    AND r.scheduled_date = CURRENT_DATE
                    AND r.status = 'sent'
                )
            """)
            
            for book in overdue_books:
                user = {
                    'id': book['user_id'],
                    'email': book['email'],
                    'first_name': book['first_name'],
                    'telegram_chat_id': book['telegram_chat_id'],
                    'preferences': book['preferences'] or {}
                }
                
                book_info = {
                    'borrowed_book_id': book['id'],
                    'title': book['title'],
                    'author': book['author'],
                    'due_date': book['due_date'].strftime('%B %d, %Y')
                }
                
                await self.notification_service.send_due_date_reminder(
                    user, book_info, -book['days_overdue']
                )
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"Error processing overdue reminders: {e}")
        finally:
            await db.close()
    
    async def process_reservation_notifications(self):
        """Notify users when their reserved books become available"""
        db = await get_database()
        
        try:
            # Find books that just became available and have active reservations
            available_reservations = await db.fetch("""
                SELECT r.*, b.title, b.author, u.email, u.first_name,
                       u.telegram_chat_id, u.preferences
                FROM reservations r
                JOIN books b ON r.book_id = b.id
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'active'
                AND r.position_in_queue = 1
                AND b.available_copies > 0
                AND NOT EXISTS (
                    SELECT 1 FROM reminders rem
                    WHERE rem.user_id = r.user_id
                    AND rem.scheduled_date = CURRENT_DATE
                    AND rem.reminder_type = 'reservation_available'
                    AND rem.status = 'sent'
                )
            """)
            
            for reservation in available_reservations:
                user = {
                    'id': reservation['user_id'],
                    'email': reservation['email'],
                    'first_name': reservation['first_name'],
                    'telegram_chat_id': reservation['telegram_chat_id'],
                    'preferences': reservation['preferences'] or {}
                }
                
                book_info = {
                    'title': reservation['title'],
                    'author': reservation['author']
                }
                
                await self.notification_service.send_reservation_notification(user, book_info)
                
                # Update reservation status
                await db.execute("""
                    UPDATE reservations 
                    SET status = 'notified', expiry_date = $1
                    WHERE id = $2
                """, date.today() + timedelta(days=1), reservation['id'])
                
                # Log the notification
                await db.execute("""
                    INSERT INTO reminders (user_id, scheduled_date, reminder_type, sent_at, status, channel)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, user['id'], date.today(), 'reservation_available', 
                     date.today(), 'sent', 'email')
                
                await asyncio.sleep(0.1)
                
        except Exception as e:
            print(f"Error processing reservation notifications: {e}")
        finally:
            await db.close()
    
    async def calculate_and_update_fines(self):
        """Calculate and update fines for overdue books"""
        db = await get_database()
        
        try:
            # Get fine per day setting
            fine_per_day = await db.fetchval(
                "SELECT setting_value::decimal FROM library_settings WHERE setting_key = 'fine_per_day'"
            ) or 1.00
            
            # Update fines for overdue books
            await db.execute("""
                UPDATE borrowed_books 
                SET fine_amount = (CURRENT_DATE - due_date) * $1
                WHERE due_date < CURRENT_DATE 
                AND status = 'borrowed'
                AND fine_amount != (CURRENT_DATE - due_date) * $1
            """, fine_per_day)
            
            print(f"Updated fines for overdue books (${fine_per_day}/day)")
            
        except Exception as e:
            print(f"Error calculating fines: {e}")
        finally:
            await db.close()
    
    async def cleanup_expired_reservations(self):
        """Remove expired reservations and update queue positions"""
        db = await get_database()
        
        try:
            # Mark expired reservations as expired
            expired_reservations = await db.fetch("""
                UPDATE reservations 
                SET status = 'expired'
                WHERE status IN ('active', 'notified')
                AND expiry_date < CURRENT_DATE
                RETURNING book_id
            """)
            
            # Update queue positions for affected books
            book_ids = list(set([r['book_id'] for r in expired_reservations]))
            
            for book_id in book_ids:
                # Get active reservations for this book
                active_reservations = await db.fetch("""
                    SELECT id FROM reservations 
                    WHERE book_id = $1 AND status = 'active'
                    ORDER BY created_at
                """, book_id)
                
                # Update queue positions
                for i, reservation in enumerate(active_reservations, 1):
                    await db.execute("""
                        UPDATE reservations 
                        SET position_in_queue = $1
                        WHERE id = $2
                    """, i, reservation['id'])
            
            print(f"Cleaned up {len(expired_reservations)} expired reservations")
            
        except Exception as e:
            print(f"Error cleaning up reservations: {e}")
        finally:
            await db.close()
    
    async def run_daily_tasks(self):
        """Run all daily reminder and maintenance tasks"""
        print("Starting daily reminder tasks...")
        
        tasks = [
            self.process_due_date_reminders(),
            self.process_reservation_notifications(),
            self.calculate_and_update_fines(),
            self.cleanup_expired_reservations()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print("Daily reminder tasks completed")

# Background task scheduler
async def start_reminder_scheduler():
    """Start the background reminder scheduler"""
    reminder_service = ReminderService()
    
    while True:
        try:
            await reminder_service.run_daily_tasks()
            # Wait 24 hours before next run
            await asyncio.sleep(24 * 60 * 60)
        except Exception as e:
            print(f"Error in reminder scheduler: {e}")
            # Wait 1 hour before retrying
            await asyncio.sleep(60 * 60)