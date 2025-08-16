// API Constants
export const API_ENDPOINTS = {
  BOOKS: '/api/books',
  CHAT: '/api/chat',
  USERS: '/api/users',
  AUTH: '/api/auth',
};

// Book Status Constants
export const BOOK_STATUS = {
  AVAILABLE: 'available',
  BORROWED: 'borrowed',
  RESERVED: 'reserved',
  MAINTENANCE: 'maintenance',
};

// Urgency Levels
export const URGENCY_LEVELS = {
  NORMAL: 'normal',
  DUE_SOON: 'due_soon',
  OVERDUE: 'overdue',
};

// Chat Response Types
export const CHAT_RESPONSE_TYPES = {
  BOOK_SEARCH: 'book_search',
  BORROWED_BOOKS: 'borrowed_books',
  RESERVATIONS: 'reservations',
  RECOMMENDATIONS: 'recommendations',
  DUE_DATES: 'due_dates',
  FINES: 'fines',
  LIBRARY_INFO: 'library_info',
  HELP: 'help',
};

// Notification Types
export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info',
};

// Library Settings
export const LIBRARY_SETTINGS = {
  MAX_BORROW_DAYS: 14,
  MAX_RENEWALS: 2,
  MAX_RESERVATIONS: 5,
  FINE_PER_DAY: 1.00,
};

// Search Filters
export const SEARCH_FILTERS = {
  GENRES: [
    'Computer Science',
    'Mathematics',
    'Engineering',
    'Physics',
    'Chemistry',
    'Biology',
    'Literature',
    'History',
    'Philosophy',
    'Business',
    'Art & Design',
    'Reference',
  ],
  AVAILABILITY: [
    { value: 'all', label: 'All Books' },
    { value: 'available', label: 'Available Only' },
  ],
};

// Quick Actions for Chat
export const QUICK_ACTIONS = [
  "Search for books on machine learning",
  "Show my borrowed books",
  "Check my due dates",
  "Recommend similar books",
  "What are the library hours?",
  "Show my fines",
  "Help me find programming books",
  "Renew my books",
];

// Navigation Items
export const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: 'home' },
  { path: '/chat', label: 'Chat Assistant', icon: 'message-circle' },
  { path: '/search', label: 'Search Books', icon: 'search' },
  { path: '/profile', label: 'Profile', icon: 'user' },
];

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'MMMM dd, yyyy',
  SHORT: 'MMM dd',
  ISO: 'yyyy-MM-dd',
  TIME: 'HH:mm',
  DATETIME: 'MMM dd, yyyy HH:mm',
};

// Storage Keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: 'libripal_user_preferences',
  CHAT_HISTORY: 'libripal_chat_history',
  SEARCH_HISTORY: 'libripal_search_history',
  THEME: 'libripal_theme',
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  NOT_FOUND: 'The requested resource was not found.',
  SERVER_ERROR: 'An unexpected error occurred. Please try again later.',
  VALIDATION_ERROR: 'Please check your input and try again.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  BOOK_BORROWED: 'Book borrowed successfully!',
  BOOK_RENEWED: 'Book renewed successfully!',
  BOOK_RETURNED: 'Book returned successfully!',
  PROFILE_UPDATED: 'Profile updated successfully!',
  RESERVATION_MADE: 'Book reserved successfully!',
  FEEDBACK_SUBMITTED: 'Thank you for your feedback!',
};

// Loading States
export const LOADING_STATES = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
};

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
  SEARCH_PAGE_SIZE: 10,
};

// Theme Colors
export const THEME_COLORS = {
  PRIMARY: '#3b82f6',
  SUCCESS: '#10b981',
  WARNING: '#f59e0b',
  ERROR: '#ef4444',
  INFO: '#6366f1',
  NEUTRAL: '#64748b',
};

// File Upload
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ['image/jpeg', 'image/png', 'image/gif'],
};

// Chat Configuration
export const CHAT_CONFIG = {
  MAX_MESSAGE_LENGTH: 1000,
  TYPING_DELAY: 1000,
  SUGGESTIONS_LIMIT: 6,
  HISTORY_LIMIT: 50,
};

// Responsive Breakpoints
export const BREAKPOINTS = {
  MOBILE: '480px',
  TABLET: '768px',
  DESKTOP: '1024px',
  WIDE: '1200px',
};

// Feature Flags
export const FEATURES = {
  ENABLE_CHAT: true,
  ENABLE_RECOMMENDATIONS: true,
  ENABLE_REVIEWS: true,
  ENABLE_NOTIFICATIONS: true,
  ENABLE_DARK_MODE: true,
  ENABLE_OFFLINE_MODE: false,
};

// External Links
export const EXTERNAL_LINKS = {
  SUPPORT: 'mailto:support@libripal.com',
  PRIVACY: '/privacy',
  TERMS: '/terms',
  GITHUB: 'https://github.com/libripal/libripal',
  DOCUMENTATION: '/docs',
};