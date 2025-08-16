import { format, parseISO, differenceInDays, isValid } from 'date-fns';
import { DATE_FORMATS, URGENCY_LEVELS, STORAGE_KEYS } from './constants';

// Date Utilities
export const formatDate = (date, formatString = DATE_FORMATS.DISPLAY) => {
  try {
    const dateObj = typeof date === 'string' ? parseISO(date) : date;
    return isValid(dateObj) ? format(dateObj, formatString) : 'Invalid date';
  } catch (error) {
    console.error('Date formatting error:', error);
    return 'Invalid date';
  }
};

export const getDaysUntilDue = (dueDate) => {
  try {
    const dateObj = typeof dueDate === 'string' ? parseISO(dueDate) : dueDate;
    return differenceInDays(dateObj, new Date());
  } catch (error) {
    return 0;
  }
};

export const getUrgencyLevel = (dueDate) => {
  const daysUntil = getDaysUntilDue(dueDate);
  
  if (daysUntil < 0) return URGENCY_LEVELS.OVERDUE;
  if (daysUntil <= 3) return URGENCY_LEVELS.DUE_SOON;
  return URGENCY_LEVELS.NORMAL;
};

export const getUrgencyColor = (urgency) => {
  switch (urgency) {
    case URGENCY_LEVELS.OVERDUE:
      return '#ef4444';
    case URGENCY_LEVELS.DUE_SOON:
      return '#f59e0b';
    default:
      return '#10b981';
  }
};

export const getUrgencyLabel = (urgency) => {
  switch (urgency) {
    case URGENCY_LEVELS.OVERDUE:
      return '🚨 Overdue';
    case URGENCY_LEVELS.DUE_SOON:
      return '⚠️ Due Soon';
    default:
      return '✅ Normal';
  }
};

// String Utilities
export const truncateText = (text, maxLength = 100, suffix = '...') => {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + suffix;
};

export const capitalizeFirst = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const slugify = (text) => {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
};

// Validation Utilities
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password) => {
  return password && password.length >= 8;
};

export const validateRequired = (value) => {
  return value !== null && value !== undefined && value !== '';
};

// Array Utilities
export const groupBy = (array, key) => {
  return array.reduce((result, item) => {
    const group = item[key];
    if (!result[group]) {
      result[group] = [];
    }
    result[group].push(item);
    return result;
  }, {});
};

export const sortBy = (array, key, direction = 'asc') => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (direction === 'desc') {
      return bVal > aVal ? 1 : -1;
    }
    return aVal > bVal ? 1 : -1;
  });
};

export const uniqueBy = (array, key) => {
  const seen = new Set();
  return array.filter(item => {
    const val = item[key];
    if (seen.has(val)) {
      return false;
    }
    seen.add(val);
    return true;
  });
};

// Search Utilities
export const highlightSearchTerm = (text, searchTerm) => {
  if (!searchTerm) return text;
  
  const regex = new RegExp(`(${searchTerm})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
};

export const fuzzySearch = (items, searchTerm, keys) => {
  if (!searchTerm) return items;
  
  const lowerSearchTerm = searchTerm.toLowerCase();
  
  return items.filter(item => {
    return keys.some(key => {
      const value = item[key];
      return value && value.toString().toLowerCase().includes(lowerSearchTerm);
    });
  });
};

// Storage Utilities
export const saveToStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch (error) {
    console.error('Error saving to storage:', error);
    return false;
  }
};

export const getFromStorage = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.error('Error reading from storage:', error);
    return defaultValue;
  }
};

export const removeFromStorage = (key) => {
  try {
    localStorage.removeItem(key);
    return true;
  } catch (error) {
    console.error('Error removing from storage:', error);
    return false;
  }
};

// URL Utilities
export const getQueryParams = () => {
  const params = new URLSearchParams(window.location.search);
  const result = {};
  for (const [key, value] of params) {
    result[key] = value;
  }
  return result;
};

export const updateQueryParams = (params) => {
  const url = new URL(window.location);
  Object.keys(params).forEach(key => {
    if (params[key] !== null && params[key] !== undefined) {
      url.searchParams.set(key, params[key]);
    } else {
      url.searchParams.delete(key);
    }
  });
  window.history.replaceState({}, '', url);
};

// Format Utilities
export const formatCurrency = (amount, currency = 'USD') => {
  try {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  } catch (error) {
    return `$${amount.toFixed(2)}`;
  }
};

export const formatNumber = (number, options = {}) => {
  try {
    return new Intl.NumberFormat('en-US', options).format(number);
  } catch (error) {
    return number.toString();
  }
};

export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Performance Utilities
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Error Handling Utilities
export const getErrorMessage = (error) => {
  if (typeof error === 'string') return error;
  if (error?.message) return error.message;
  if (error?.detail) return error.detail;
  return 'An unexpected error occurred';
};

export const isNetworkError = (error) => {
  return error?.name === 'TypeError' && error?.message?.includes('fetch');
};

// Book Utilities
export const getBookCoverPlaceholder = (title) => {
  const encoded = encodeURIComponent(title);
  return `https://via.placeholder.com/300x450/3b82f6/ffffff?text=${encoded}`;
};

export const generateBookSlug = (title, author) => {
  return slugify(`${title} ${author}`);
};

export const extractBookKeywords = (title, author, description = '') => {
  const text = `${title} ${author} ${description}`.toLowerCase();
  const words = text.match(/\b\w+\b/g) || [];
  
  // Filter out common words
  const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']);
  
  return [...new Set(words.filter(word => word.length > 2 && !stopWords.has(word)))].slice(0, 10);
};

// Chat Utilities
export const formatChatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  
  return formatDate(date, 'MMM dd');
};

export const isValidChatMessage = (message) => {
  return message && message.trim().length > 0 && message.length <= 1000;
};

// Accessibility Utilities
export const generateId = (prefix = 'id') => {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

export const announceToScreenReader = (message) => {
  const announcement = document.createElement('div');
  announcement.setAttribute('aria-live', 'polite');
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;
  
  document.body.appendChild(announcement);
  setTimeout(() => document.body.removeChild(announcement), 1000);
};

// Development Utilities
export const isDevelopment = () => {
  return process.env.NODE_ENV === 'development';
};

export const log = (...args) => {
  if (isDevelopment()) {
    console.log('[LibriPal]', ...args);
  }
};

export const logError = (...args) => {
  if (isDevelopment()) {
    console.error('[LibriPal Error]', ...args);
  }
};