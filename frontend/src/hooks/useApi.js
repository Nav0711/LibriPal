import { useState, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const useApi = () => {
  const { getToken } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const apiCall = useCallback(async (endpoint, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const token = await getToken();
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [getToken]);

  return { apiCall, loading, error };
};

// Specific API hooks for different features
export const useBooks = () => {
  const { apiCall } = useApi();

  const searchBooks = useCallback(async (query, filters = {}) => {
    return apiCall('/api/books/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        limit: 20,
        ...filters
      })
    });
  }, [apiCall]);

  const getBook = useCallback(async (bookId) => {
    return apiCall(`/api/books/${bookId}`);
  }, [apiCall]);

  const borrowBook = useCallback(async (bookId) => {
    return apiCall('/api/books/borrow', {
      method: 'POST',
      body: JSON.stringify({ book_id: bookId })
    });
  }, [apiCall]);

  const renewBook = useCallback(async (borrowedBookId) => {
    return apiCall('/api/books/renew', {
      method: 'POST',
      body: JSON.stringify({ borrowed_book_id: borrowedBookId })
    });
  }, [apiCall]);

  const returnBook = useCallback(async (bookId) => {
    return apiCall(`/api/books/${bookId}/return`, {
      method: 'POST'
    });
  }, [apiCall]);

  return {
    searchBooks,
    getBook,
    borrowBook,
    renewBook,
    returnBook
  };
};

export const useUserData = () => {
  const { apiCall } = useApi();

  const getUserProfile = useCallback(async () => {
    return apiCall('/api/users/profile');
  }, [apiCall]);

  const updateProfile = useCallback(async (profileData) => {
    return apiCall('/api/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  }, [apiCall]);

  const getBorrowedBooks = useCallback(async () => {
    return apiCall('/api/users/borrowed');
  }, [apiCall]);

  const getReservations = useCallback(async () => {
    return apiCall('/api/users/reservations');
  }, [apiCall]);

  const getFines = useCallback(async () => {
    return apiCall('/api/users/fines');
  }, [apiCall]);

  const getReadingHistory = useCallback(async (limit = 50) => {
    return apiCall(`/api/users/reading-history?limit=${limit}`);
  }, [apiCall]);

  const getStatistics = useCallback(async () => {
    return apiCall('/api/users/statistics');
  }, [apiCall]);

  return {
    getUserProfile,
    updateProfile,
    getBorrowedBooks,
    getReservations,
    getFines,
    getReadingHistory,
    getStatistics
  };
};

export const useChat = () => {
  const { apiCall } = useApi();

  const sendMessage = useCallback(async (message, context = null) => {
    return apiCall('/api/chat/', {
      method: 'POST',
      body: JSON.stringify({
        message,
        context
      })
    });
  }, [apiCall]);

  const getSuggestions = useCallback(async () => {
    return apiCall('/api/chat/suggestions');
  }, [apiCall]);

  const submitFeedback = useCallback(async (feedbackData) => {
    return apiCall('/api/chat/feedback', {
      method: 'POST',
      body: JSON.stringify(feedbackData)
    });
  }, [apiCall]);

  return {
    sendMessage,
    getSuggestions,
    submitFeedback
  };
};