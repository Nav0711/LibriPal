-- Migration 001: Initial Tables
-- Created: 2025-08-16
-- Description: Create initial database tables

BEGIN;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    telegram_chat_id VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create books table
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(500) NOT NULL,
    publisher VARCHAR(255),
    publication_year INTEGER,
    genre VARCHAR(100),
    description TEXT,
    total_copies INTEGER DEFAULT 1,
    available_copies INTEGER DEFAULT 1,
    cover_image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create borrowed_books table
CREATE TABLE borrowed_books (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    borrowed_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    returned_date DATE,
    renewal_count INTEGER DEFAULT 0,
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'borrowed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reservations table
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    reservation_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    status VARCHAR(50) DEFAULT 'active',
    position_in_queue INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create basic indexes
CREATE INDEX idx_users_clerk_id ON users(clerk_id);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_borrowed_books_user_id ON borrowed_books(user_id);
CREATE INDEX idx_borrowed_books_due_date ON borrowed_books(due_date);

COMMIT;