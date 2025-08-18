#!/usr/bin/env python3
"""
Data seeding script for LibriPal
This script populates the database with sample data for development and testing.
"""

import asyncio
import asyncpg
import os
import sys
import json
from pathlib import Path
from datetime import date, timedelta
import random

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://libripal_user:password@localhost:5432/libripal")

# Sample data
SAMPLE_USERS = [
    {
        "clerk_id": "user_demo_student1",
        "email": "alice.student@university.edu",
        "first_name": "Alice",
        "last_name": "Johnson",
        "preferences": {"email_reminders": True, "telegram_reminders": False}
    },
    {
        "clerk_id": "user_demo_student2", 
        "email": "bob.researcher@university.edu",
        "first_name": "Bob",
        "last_name": "Smith",
        "preferences": {"email_reminders": True, "telegram_reminders": True}
    },
    {
        "clerk_id": "user_demo_faculty1",
        "email": "dr.wilson@university.edu", 
        "first_name": "Dr. Sarah",
        "last_name": "Wilson",
        "preferences": {"email_reminders": False, "telegram_reminders": True}
    }
]

ADDITIONAL_BOOKS = [
    {
        "isbn": "9780596009205",
        "title": "Head First Design Patterns",
        "author": "Eric Freeman, Elisabeth Robson",
        "publisher": "O'Reilly Media",
        "publication_year": 2004,
        "genre": "Computer Science",
        "description": "A brain-friendly guide to design patterns in object-oriented programming.",
        "total_copies": 2,
        "available_copies": 1
    },
    {
        "isbn": "9780134494166",
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "publisher": "Prentice Hall",
        "publication_year": 2017,
        "genre": "Computer Science", 
        "description": "A comprehensive guide to software architecture and design principles.",
        "total_copies": 3,
        "available_copies": 2
    },
    {
        "isbn": "9781449355739",
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "publisher": "O'Reilly Media",
        "publication_year": 2017,
        "genre": "Computer Science",
        "description": "The big ideas behind reliable, scalable, and maintainable systems.",
        "total_copies": 2,
        "available_copies": 0
    },
    {
        "isbn": "9780321573513",
        "title": "Algorithms",
        "author": "Robert Sedgewick, Kevin Wayne",
        "publisher": "Addison-Wesley",
        "publication_year": 2011,
        "genre": "Computer Science",
        "description": "Essential information that every serious programmer needs to know about algorithms.",
        "total_copies": 4,
        "available_copies": 3
    },
    {
        "isbn": "9780134052502",
        "title": "The Art of Computer Programming, Volume 1",
        "author": "Donald E. Knuth",
        "publisher": "Addison-Wesley",
        "publication_year": 2011,
        "genre": "Computer Science",
        "description": "Fundamental algorithms and data structures.",
        "total_copies": 2,
        "available_copies": 2
    }
]

async def seed_users(conn):
    """Seed sample users"""
    print("👥 Seeding sample users...")
    
    for user_data in SAMPLE_USERS:
        try:
            await conn.execute("""
                INSERT INTO users (clerk_id, email, first_name, last_name, preferences)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (clerk_id) DO NOTHING
            """, 
            user_data["clerk_id"],
            user_data["email"],
            user_data["first_name"], 
            user_data["last_name"],
            json.dumps(user_data["preferences"])
            )
            print(f"  ✅ Created user: {user_data['first_name']} {user_data['last_name']}")
        except Exception as e:
            print(f"  ❌ Error creating user {user_data['email']}: {e}")

async def seed_additional_books(conn):
    """Seed additional books"""
    print("📚 Seeding additional books...")
    
    for book_data in ADDITIONAL_BOOKS:
        try:
            await conn.execute("""
                INSERT INTO books (isbn, title, author, publisher, publication_year, genre, description, total_copies, available_copies)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (isbn) DO NOTHING
            """,
            book_data["isbn"],
            book_data["title"],
            book_data["author"],
            book_data["publisher"],
            book_data["publication_year"],
            book_data["genre"],
            book_data["description"],
            book_data["total_copies"],
            book_data["available_copies"]
            )
            print(f"  ✅ Added book: {book_data['title']}")
        except Exception as e:
            print(f"  ❌ Error adding book {book_data['title']}: {e}")

async def seed_borrowed_books(conn):
    """Create some borrowed books for testing"""
    print("📖 Creating sample borrowed books...")
    
    # Get users and books
    users = await conn.fetch("SELECT id FROM users LIMIT 3")
    books = await conn.fetch("SELECT id FROM books WHERE available_copies > 0 LIMIT 5")
    
    if not users or not books:
        print("  ⚠️ No users or books available for borrowing simulation")
        return
    
    borrowings = [
        (users[0]['id'], books[0]['id'], 3),  # Due in 3 days (due soon)
        (users[0]['id'], books[1]['id'], 10), # Due in 10 days (normal)
        (users[1]['id'], books[2]['id'], -2), # Overdue by 2 days
        (users[1]['id'], books[3]['id'], 7),  # Due in 7 days (normal)
        (users[2]['id'], books[4]['id'], 1),  # Due tomorrow (due soon)
    ]
    
    for user_id, book_id, days_until_due in borrowings:
        due_date = date.today() + timedelta(days=days_until_due)
        borrowed_date = due_date - timedelta(days=14)  # 14-day loan period
        
        try:
            await conn.execute("""
                INSERT INTO borrowed_books (user_id, book_id, borrowed_date, due_date, renewal_count)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, book_id, borrowed_date, due_date, random.randint(0, 2))
            
            # Update available copies
            await conn.execute("""
                UPDATE books SET available_copies = available_copies - 1 WHERE id = $1
            """, book_id)
            
            print(f"  ✅ Created borrowing: User {user_id} borrowed Book {book_id}")
            
        except Exception as e:
            print(f"  ❌ Error creating borrowing: {e}")

async def seed_reservations(conn):
    """Create some reservations for testing"""
    print("📋 Creating sample reservations...")
    
    # Get users and books with no available copies
    users = await conn.fetch("SELECT id FROM users")
    unavailable_books = await conn.fetch("SELECT id FROM books WHERE available_copies = 0")
    
    if not users or not unavailable_books:
        print("  ⚠️ No suitable books for reservation simulation")
        return
    
    # Create a few reservations
    for i, user in enumerate(users[:2]):
        if i < len(unavailable_books):
            book_id = unavailable_books[i]['id']
            try:
                await conn.execute("""
                    INSERT INTO reservations (user_id, book_id, position_in_queue, expiry_date)
                    VALUES ($1, $2, $3, $4)
                """, user['id'], book_id, i + 1, date.today() + timedelta(days=7))
                
                print(f"  ✅ Created reservation: User {user['id']} reserved Book {book_id}")
                
            except Exception as e:
                print(f"  ❌ Error creating reservation: {e}")

async def seed_search_history(conn):
    """Create sample search history"""
    print("🔍 Creating sample search history...")
    
    users = await conn.fetch("SELECT id FROM users")
    
    search_queries = [
        "python programming",
        "machine learning",
        "data structures",
        "web development",
        "algorithms",
        "database design",
        "software engineering",
        "artificial intelligence",
        "computer networks",
        "cybersecurity"
    ]
    
    for user in users:
        # Create 5-8 search history entries per user
        num_searches = random.randint(5, 8)
        for _ in range(num_searches):
            query = random.choice(search_queries)
            search_type = random.choice(["book_search", "chat", "recommendation"])
            results_count = random.randint(0, 15)
            
            try:
                await conn.execute("""
                    INSERT INTO search_history (user_id, search_query, search_type, results_count)
                    VALUES ($1, $2, $3, $4)
                """, user['id'], query, search_type, results_count)
                
            except Exception as e:
                print(f"  ❌ Error creating search history: {e}")
    
    print(f"  ✅ Created search history for {len(users)} users")

async def seed_book_reviews(conn):
    """Create sample book reviews"""
    print("⭐ Creating sample book reviews...")
    
    users = await conn.fetch("SELECT id FROM users")
    books = await conn.fetch("SELECT id FROM books LIMIT 10")
    
    reviews = [
        "Excellent book! Very comprehensive and well-written.",
        "Good introduction to the topic, but could use more examples.",
        "A bit outdated, but still relevant for understanding fundamentals.",
        "Perfect for beginners. Clear explanations and practical exercises.",
        "Advanced material. Requires solid background knowledge.",
        "Well-structured content with good real-world applications.",
        "Somewhat dry reading, but informative and accurate.",
        "Great reference book. Very detailed and thorough.",
        "Easy to follow examples. Highly recommended!",
        "Could be better organized, but contains valuable information."
    ]
    
    # Create reviews for some books
    for book in books[:7]:  # Review first 7 books
        # Randomly assign 1-3 reviews per book
        num_reviews = random.randint(1, 3)
        selected_users = random.sample(users, min(num_reviews, len(users)))
        
        for user in selected_users:
            rating = random.randint(3, 5)  # Mostly positive ratings
            review_text = random.choice(reviews)
            
            try:
                await conn.execute("""
                    INSERT INTO book_reviews (user_id, book_id, rating, review_text, is_verified_borrower)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id, book_id) DO NOTHING
                """, user['id'], book['id'], rating, review_text, random.choice([True, False]))
                
            except Exception as e:
                print(f"  ❌ Error creating review: {e}")
    
    print(f"  ✅ Created reviews for books")

async def seed_notifications(conn):
    """Create sample system notifications"""
    print("🔔 Creating sample notifications...")
    
    notifications = [
        {
            "title": "Welcome to LibriPal!",
            "message": "Your AI-powered library assistant is ready to help you manage your books efficiently.",
            "notification_type": "info",
            "target_audience": "all"
        },
        {
            "title": "New Books Added",
            "message": "We've added 50 new computer science books to our collection. Check them out!",
            "notification_type": "success", 
            "target_audience": "all"
        },
        {
            "title": "Maintenance Notice",
            "message": "The library system will undergo maintenance on Sunday from 2:00 AM to 4:00 AM.",
            "notification_type": "warning",
            "target_audience": "all"
        }
    ]
    
    for notif in notifications:
        try:
            await conn.execute("""
                INSERT INTO system_notifications (title, message, notification_type, target_audience, expires_at)
                VALUES ($1, $2, $3, $4, $5)
            """, 
            notif["title"], 
            notif["message"], 
            notif["notification_type"],
            notif["target_audience"],
            date.today() + timedelta(days=30)
            )
            print(f"  ✅ Created notification: {notif['title']}")
            
        except Exception as e:
            print(f"  ❌ Error creating notification: {e}")

async def seed_all_data():
    """Seed all sample data"""
    print("🌱 Starting data seeding process...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Seed data in order
        await seed_users(conn)
        await seed_additional_books(conn)
        await seed_borrowed_books(conn)
        await seed_reservations(conn)
        await seed_search_history(conn)
        await seed_book_reviews(conn)
        await seed_notifications(conn)
        
        await conn.close()
        print("🎉 Data seeding completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during data seeding: {e}")
        return False

async def clear_sample_data():
    """Clear all sample data (keep schema)"""
    print("🧹 Clearing sample data...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Delete in reverse order of dependencies
        tables_to_clear = [
            "chat_feedback",
            "system_notifications", 
            "book_reviews",
            "reading_list_items",
            "reading_lists",
            "book_category_mappings",
            "search_history",
            "reminders",
            "reservations",
            "borrowed_books",
            "user_notification_settings",
            "users",
            "books",
            "book_categories"
        ]
        
        for table in tables_to_clear:
            await conn.execute(f"DELETE FROM {table}")
            print(f"  ✅ Cleared {table}")
        
        # Reset sequences
        await conn.execute("SELECT setval(pg_get_serial_sequence('users', 'id'), 1, false)")
        await conn.execute("SELECT setval(pg_get_serial_sequence('books', 'id'), 1, false)")
        
        await conn.close()
        print("✅ Sample data cleared successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing data: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LibriPal Data Seeding")
    parser.add_argument(
        "action",
        choices=["seed", "clear"],
        help="Action to perform"
    )
    
    args = parser.parse_args()
    
    if args.action == "seed":
        success = asyncio.run(seed_all_data())
    elif args.action == "clear":
        confirm = input("⚠️ This will delete all sample data. Are you sure? (yes/no): ")
        if confirm.lower() == "yes":
            success = asyncio.run(clear_sample_data())
        else:
            print("❌ Clear operation cancelled")
            return
    
    if success:
        print("🎉 Operation completed successfully!")
    else:
        print("💥 Operation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()