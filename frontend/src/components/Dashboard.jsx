import React, { useState, useEffect } from 'react';
import { Book, Calendar, AlertCircle, TrendingUp } from 'lucide-react';

const Dashboard = ({ apiCall }) => {
  const [stats, setStats] = useState({
    borrowedBooks: [],
    upcomingDues: [],
    fines: { total_amount: 0, fines: [] },
    recommendations: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [borrowed, fines, recommendations] = await Promise.all([
          apiCall('/borrowed'),
          apiCall('/fines'),
          apiCall('/recommendations')
        ]);

        const upcomingDues = borrowed.borrowed_books.filter(book => 
          book.urgency === 'due_soon' || book.urgency === 'overdue'
        );

        setStats({
          borrowedBooks: borrowed.borrowed_books,
          upcomingDues,
          fines,
          recommendations: recommendations.recommendations
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [apiCall]);

  const handleRenewBook = async (borrowedBookId) => {
    try {
      await apiCall('/renew', {
        method: 'POST',
        body: JSON.stringify({ borrowed_book_id: borrowedBookId })
      });
      
      // Refresh data
      window.location.reload();
    } catch (error) {
      alert('Error renewing book: ' + error.message);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your library dashboard...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <h1>📚 LibriPal Dashboard</h1>
      
      {/* Stats Overview */}
      <div className="stats-grid">
        <div className="stat-card">
          <Book className="stat-icon" />
          <div>
            <h3>{stats.borrowedBooks.length}</h3>
            <p>Books Borrowed</p>
          </div>
        </div>
        
        <div className="stat-card">
          <Calendar className="stat-icon" />
          <div>
            <h3>{stats.upcomingDues.length}</h3>
            <p>Due Soon</p>
          </div>
        </div>
        
        <div className="stat-card">
          <AlertCircle className="stat-icon" />
          <div>
            <h3>${stats.fines.total_amount.toFixed(2)}</h3>
            <p>Outstanding Fines</p>
          </div>
        </div>
        
        <div className="stat-card">
          <TrendingUp className="stat-icon" />
          <div>
            <h3>{stats.recommendations.length}</h3>
            <p>Recommendations</p>
          </div>
        </div>
      </div>

      {/* Upcoming Due Dates */}
      {stats.upcomingDues.length > 0 && (
        <div className="dashboard-section">
          <h2>⚠️ Books Due Soon</h2>
          <div className="books-grid">
            {stats.upcomingDues.map(book => (
              <div key={book.id} className={`book-card ${book.urgency}`}>
                <img 
                  src={book.cover_image_url || '/placeholder-book.png'} 
                  alt={book.title}
                  className="book-cover"
                />
                <div className="book-info">
                  <h4>{book.title}</h4>
                  <p>by {book.author}</p>
                  <p className="due-date">Due: {new Date(book.due_date).toLocaleDateString()}</p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => handleRenewBook(book.id)}
                  >
                    Renew
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Current Borrowed Books */}
      <div className="dashboard-section">
        <h2>📖 Currently Borrowed</h2>
        {stats.borrowedBooks.length === 0 ? (
          <p>No books currently borrowed. <a href="/search">Search for books</a> to get started!</p>
        ) : (
          <div className="books-grid">
            {stats.borrowedBooks.map(book => (
              <div key={book.id} className="book-card">
                <img 
                  src={book.cover_image_url || '/placeholder-book.png'} 
                  alt={book.title}
                  className="book-cover"
                />
                <div className="book-info">
                  <h4>{book.title}</h4>
                  <p>by {book.author}</p>
                  <p>Due: {new Date(book.due_date).toLocaleDateString()}</p>
                  <p>Renewals: {book.renewal_count}/2</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recommendations */}
      {stats.recommendations.length > 0 && (
        <div className="dashboard-section">
          <h2>💡 Recommended for You</h2>
          <div className="books-grid">
            {stats.recommendations.slice(0, 4).map(book => (
              <div key={book.id} className="book-card">
                <img 
                  src={book.cover_image_url || '/placeholder-book.png'} 
                  alt={book.title}
                  className="book-cover"
                />
                <div className="book-info">
                  <h4>{book.title}</h4>
                  <p>by {book.author}</p>
                  {book.ai_summary && <p className="book-summary">{book.ai_summary}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;