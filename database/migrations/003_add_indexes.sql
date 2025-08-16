-- Migration 003: Add Performance Indexes
-- Created: 2025-08-16
-- Description: Add additional indexes for better performance

BEGIN;

-- Add missing indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_available_copies ON books(available_copies);

CREATE INDEX IF NOT EXISTS idx_borrowed_books_book_id ON borrowed_books(book_id);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_status ON borrowed_books(status);

CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_book_id ON reservations(book_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);

CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);

-- Add composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_borrowed_books_user_status ON borrowed_books(user_id, status);
CREATE INDEX IF NOT EXISTS idx_reservations_book_status ON reservations(book_id, status);

-- Add updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add updated_at column where missing and create triggers
ALTER TABLE books ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE borrowed_books ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE reservations ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT;