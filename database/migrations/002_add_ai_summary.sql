-- Migration 002: Add AI Summary and Enhanced Features
-- Created: 2025-08-16
-- Description: Add AI summary field and search improvements

BEGIN;

-- Add AI summary column to books
ALTER TABLE books ADD COLUMN ai_summary TEXT;

-- Add full-text search indexes
CREATE INDEX idx_books_title_fts ON books USING GIN(to_tsvector('english', title));
CREATE INDEX idx_books_author_fts ON books USING GIN(to_tsvector('english', author));
CREATE INDEX idx_books_description_fts ON books USING GIN(to_tsvector('english', description));

-- Create reminders table
CREATE TABLE reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    borrowed_book_id INTEGER REFERENCES borrowed_books(id) ON DELETE CASCADE,
    reminder_type VARCHAR(50) NOT NULL,
    scheduled_date DATE NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    channel VARCHAR(50) DEFAULT 'email',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create search history table
CREATE TABLE search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    search_type VARCHAR(50),
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create library settings table
CREATE TABLE library_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes
CREATE INDEX idx_reminders_scheduled_date ON reminders(scheduled_date);
CREATE INDEX idx_search_history_user_id ON search_history(user_id);

COMMIT;