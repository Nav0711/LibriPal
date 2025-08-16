-- Library Settings Data
-- Created: 2025-08-16

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
('library_address', '123 University Ave, Academic City, AC 12345', 'Physical address of library', TRUE),
('library_phone', '+1-555-LIBRARY (555-542-7279)', 'Library contact phone', TRUE),
('library_email', 'info@libripal.com', 'Library contact email', TRUE),
('auto_renew_enabled', 'false', 'Enable automatic renewal if no holds', FALSE),
('late_fee_grace_period', '2', 'Grace period in days before fines start', TRUE),
('notification_email_from', 'LibriPal <noreply@libripal.com>', 'From address for email notifications', FALSE),
('max_search_results', '50', 'Maximum number of search results to return', TRUE),
('enable_ai_recommendations', 'true', 'Enable AI-powered book recommendations', TRUE),
('enable_chat_interface', 'true', 'Enable the chat interface', TRUE),
('maintenance_mode', 'false', 'Enable maintenance mode', FALSE),
('welcome_message', 'Welcome to LibriPal! Your AI-powered library assistant.', 'Welcome message for new users', TRUE)
ON CONFLICT (setting_key) DO NOTHING;