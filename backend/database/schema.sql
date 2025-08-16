-- LibriPal Database Schema
-- Created: 2025-08-16
-- Description: Complete database schema for LibriPal library management system

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    telegram_chat_id VARCHAR(100),
    preferences JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE IF NOT EXISTS books (
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
    ai_summary TEXT,
    reading_level VARCHAR(50),
    keywords TEXT[],
    status VARCHAR(50) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Borrowed books table
CREATE TABLE IF NOT EXISTS borrowed_books (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    borrowed_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    returned_date DATE,
    renewal_count INTEGER DEFAULT 0,
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    status VARCHAR(50) DEFAULT 'borrowed', -- borrowed, returned, overdue
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reservations table
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    reservation_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    status VARCHAR(50) DEFAULT 'active', -- active, fulfilled, expired, cancelled
    position_in_queue INTEGER,
    notified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reminders table
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    borrowed_book_id INTEGER REFERENCES borrowed_books(id) ON DELETE SET NULL,
    reminder_type VARCHAR(50) NOT NULL, -- '3_day', '1_day', 'overdue', 'reservation_available'
    scheduled_date DATE NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, failed
    channel VARCHAR(50) DEFAULT 'email', -- email, telegram, both
    message_content TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search history table
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    search_type VARCHAR(50), -- 'book_search', 'topic_qa', 'recommendation', 'chat'
    results_count INTEGER DEFAULT 0,
    filters_applied JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat feedback table (for AI improvement)
CREATE TABLE IF NOT EXISTS chat_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response_type VARCHAR(50),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Library settings table
CREATE TABLE IF NOT EXISTS library_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    updated_by INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Book categories table (for better organization)
CREATE TABLE IF NOT EXISTS book_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_category_id INTEGER REFERENCES book_categories(id),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Book category mappings
CREATE TABLE IF NOT EXISTS book_category_mappings (
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES book_categories(id) ON DELETE CASCADE,
    PRIMARY KEY (book_id, category_id)
);

-- User reading lists (favorites, want-to-read, etc.)
CREATE TABLE IF NOT EXISTS reading_lists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Reading list items
CREATE TABLE IF NOT EXISTS reading_list_items (
    id SERIAL PRIMARY KEY,
    reading_list_id INTEGER REFERENCES reading_lists(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(reading_list_id, book_id)
);

-- Book reviews and ratings
CREATE TABLE IF NOT EXISTS book_reviews (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    is_verified_borrower BOOLEAN DEFAULT FALSE,
    helpful_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id)
);

-- System notifications
CREATE TABLE IF NOT EXISTS system_notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'info', -- info, warning, error, success
    target_audience VARCHAR(50) DEFAULT 'all', -- all, admins, users
    is_active BOOLEAN DEFAULT TRUE,
    starts_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User notification preferences (detailed)
CREATE TABLE IF NOT EXISTS user_notification_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    email_due_reminders BOOLEAN DEFAULT TRUE,
    email_reservation_updates BOOLEAN DEFAULT TRUE,
    email_new_books BOOLEAN DEFAULT FALSE,
    email_recommendations BOOLEAN DEFAULT TRUE,
    telegram_due_reminders BOOLEAN DEFAULT FALSE,
    telegram_reservation_updates BOOLEAN DEFAULT FALSE,
    telegram_new_books BOOLEAN DEFAULT FALSE,
    reminder_days_before INTEGER[] DEFAULT ARRAY[3, 1],
    quiet_hours_start TIME DEFAULT '22:00',
    quiet_hours_end TIME DEFAULT '08:00',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for important actions
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- 'book_borrowed', 'book_returned', 'fine_paid', etc.
    resource_type VARCHAR(50), -- 'book', 'user', 'reservation', etc.
    resource_id INTEGER,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Insert default library settings
INSERT INTO library_settings (setting_key, setting_value, description, is_public) VALUES
('max_borrow_days', '14', 'Maximum days a book can be borrowed', TRUE),
('max_renewals', '2', 'Maximum number of renewals allowed per book', TRUE),
('fine_per_day', '1.00', 'Fine amount per day for overdue books', TRUE),
('max_reservations_per_user', '5', 'Maximum reservations per user', TRUE),
('max_books_per_user', '10', 'Maximum books a user can borrow simultaneously', TRUE),
('reservation_hold_days', '7', 'Days to hold a reserved book before expiry', TRUE),
('library_opening_hours', '{"monday": "9:00-18:00", "tuesday": "9:00-18:00", "wednesday": "9:00-18:00", "thursday": "9:00-18:00", "friday": "9:00-18:00", "saturday": "10:00-16:00", "sunday": "closed"}', 'Library opening hours', TRUE),
('reminder_days', '[3, 1]', 'Days before due date to send reminders', TRUE),
('library_name', 'LibriPal Digital Library', 'Name of the library', TRUE),
('library_address', '123 University Ave, Academic City', 'Physical address of library', TRUE),
('library_phone', '+1-555-LIBRARY', 'Library contact phone', TRUE),
('library_email', 'info@libripal.com', 'Library contact email', TRUE),
('auto_renew_enabled', 'false', 'Enable automatic renewal if no holds', FALSE),
('late_fee_grace_period', '2', 'Grace period in days before fines start', TRUE)
ON CONFLICT (setting_key) DO NOTHING;

-- Insert default book categories
INSERT INTO book_categories (name, description, display_order) VALUES
('Computer Science', 'Programming, algorithms, software engineering', 1),
('Mathematics', 'Pure and applied mathematics, statistics', 2),
('Engineering', 'All engineering disciplines', 3),
('Physics', 'Theoretical and applied physics', 4),
('Chemistry', 'Organic, inorganic, and analytical chemistry', 5),
('Biology', 'Life sciences, genetics, ecology', 6),
('Literature', 'Fiction, poetry, literary criticism', 7),
('History', 'World history, regional studies', 8),
('Philosophy', 'Ethics, logic, metaphysics', 9),
('Business', 'Management, economics, finance', 10),
('Art & Design', 'Visual arts, graphic design, architecture', 11),
('Reference', 'Dictionaries, encyclopedias, handbooks', 12)
ON CONFLICT (name) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_clerk_id ON users(clerk_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_telegram_chat_id ON users(telegram_chat_id);

CREATE INDEX IF NOT EXISTS idx_books_title ON books USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_books_author ON books USING GIN(to_tsvector('english', author));
CREATE INDEX IF NOT EXISTS idx_books_description ON books USING GIN(to_tsvector('english', description));
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre);
CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
CREATE INDEX IF NOT EXISTS idx_books_available_copies ON books(available_copies);

CREATE INDEX IF NOT EXISTS idx_borrowed_books_user_id ON borrowed_books(user_id);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_book_id ON borrowed_books(book_id);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_due_date ON borrowed_books(due_date);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_status ON borrowed_books(status);
CREATE INDEX IF NOT EXISTS idx_borrowed_books_returned_date ON borrowed_books(returned_date);

CREATE INDEX IF NOT EXISTS idx_reservations_user_id ON reservations(user_id);
CREATE INDEX IF NOT EXISTS idx_reservations_book_id ON reservations(book_id);
CREATE INDEX IF NOT EXISTS idx_reservations_status ON reservations(status);
CREATE INDEX IF NOT EXISTS idx_reservations_queue_position ON reservations(book_id, position_in_queue);

CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_scheduled_date ON reminders(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status);
CREATE INDEX IF NOT EXISTS idx_reminders_type ON reminders(reminder_type);

CREATE INDEX IF NOT EXISTS idx_search_history_user_id ON search_history(user_id);
CREATE INDEX IF NOT EXISTS idx_search_history_created_at ON search_history(created_at);

CREATE INDEX IF NOT EXISTS idx_book_reviews_book_id ON book_reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_book_reviews_rating ON book_reviews(rating);

-- Create triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_borrowed_books_updated_at BEFORE UPDATE ON borrowed_books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reservations_updated_at BEFORE UPDATE ON reservations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW user_book_stats AS
SELECT 
    u.id as user_id,
    u.first_name,
    u.last_name,
    u.email,
    COUNT(bb.id) FILTER (WHERE bb.status = 'borrowed') as currently_borrowed,
    COUNT(bb.id) FILTER (WHERE bb.status = 'returned') as total_borrowed,
    COUNT(r.id) FILTER (WHERE r.status = 'active') as active_reservations,
    COALESCE(SUM(bb.fine_amount), 0) as total_fines,
    MAX(bb.borrowed_date) as last_borrow_date
FROM users u
LEFT JOIN borrowed_books bb ON u.id = bb.user_id
LEFT JOIN reservations r ON u.id = r.user_id
GROUP BY u.id, u.first_name, u.last_name, u.email;

CREATE OR REPLACE VIEW book_popularity AS
SELECT 
    b.id,
    b.title,
    b.author,
    b.genre,
    COUNT(bb.id) as total_borrows,
    COUNT(bb.id) FILTER (WHERE bb.status = 'borrowed') as currently_borrowed,
    COUNT(r.id) FILTER (WHERE r.status = 'active') as active_reservations,
    COALESCE(AVG(br.rating), 0) as average_rating,
    COUNT(br.id) as review_count
FROM books b
LEFT JOIN borrowed_books bb ON b.id = bb.book_id
LEFT JOIN reservations r ON b.id = r.book_id
LEFT JOIN book_reviews br ON b.id = br.book_id
GROUP BY b.id, b.title, b.author, b.genre;

CREATE OR REPLACE VIEW overdue_books AS
SELECT 
    bb.id as borrowed_book_id,
    bb.user_id,
    u.first_name,
    u.last_name,
    u.email,
    u.telegram_chat_id,
    bb.book_id,
    b.title,
    b.author,
    bb.borrowed_date,
    bb.due_date,
    CURRENT_DATE - bb.due_date as days_overdue,
    bb.fine_amount,
    bb.renewal_count
FROM borrowed_books bb
JOIN users u ON bb.user_id = u.id
JOIN books b ON bb.book_id = b.id
WHERE bb.due_date < CURRENT_DATE 
AND bb.status = 'borrowed';