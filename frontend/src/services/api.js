const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Books API
  async searchBooks(query, filters = {}) {
    return this.request('/api/books/search', {
      method: 'POST',
      body: JSON.stringify({ query, ...filters }),
    });
  }

  async getBook(bookId) {
    return this.request(`/api/books/${bookId}`);
  }

  async getBooks(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return this.request(`/api/books/?${queryString}`);
  }

  async borrowBook(bookId, token) {
    return this.request('/api/books/borrow', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ book_id: bookId }),
    });
  }

  async renewBook(borrowedBookId, token) {
    return this.request('/api/books/renew', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ borrowed_book_id: borrowedBookId }),
    });
  }

  async reserveBook(bookId, token) {
    return this.request('/api/books/reserve', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ book_id: bookId }),
    });
  }

  // Chat API
  async sendChatMessage(message, context = null, token) {
    return this.request('/api/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ message, context }),
    });
  }

  async getChatSuggestions(token) {
    return this.request('/api/chat/suggestions', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // User API
  async getUserProfile(token) {
    return this.request('/api/users/profile', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async updateUserProfile(profileData, token) {
    return this.request('/api/users/profile', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(profileData),
    });
  }

  async getBorrowedBooks(token) {
    return this.request('/api/users/borrowed', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async getReservations(token) {
    return this.request('/api/users/reservations', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async getFines(token) {
    return this.request('/api/users/fines', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async getReadingHistory(token, limit = 50) {
    return this.request(`/api/users/reading-history?limit=${limit}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  async getUserStatistics(token) {
    return this.request('/api/users/statistics', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  }

  // System API
  async getGenres() {
    return this.request('/api/books/genres/list');
  }

  async getAuthors() {
    return this.request('/api/books/authors/list');
  }

  async getHealthCheck() {
    return this.request('/health');
  }
}

export const apiService = new ApiService();
export default apiService;