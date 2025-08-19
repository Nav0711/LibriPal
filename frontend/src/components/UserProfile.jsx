"use client"

import { useState, useEffect } from "react"
import { Save, Bell, Book, AlertTriangle, Calendar, RotateCcw } from "lucide-react"

const UserProfile = ({ apiCall }) => {
  const [profile, setProfile] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    library_stats: {
      books_issued: 0,
      books_overdue: 0,
      total_fine: 0,
      max_books_allowed: 5
    },
    preferences: {
      email_reminders: true,
      fine_notifications: true
    }
  })
  const [issuedBooks, setIssuedBooks] = useState([])
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileData, booksData, notificationsData] = await Promise.all([
          apiCall("/api/users/profile"),
          apiCall("/api/users/issued-books"),
          apiCall("/api/users/notifications")
        ])
        
        setProfile(profileData)
        setIssuedBooks(booksData.issued_books || [])
        setNotifications(notificationsData.notifications || [])
      } catch (error) {
        console.error("Error fetching profile data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [apiCall])

  const handleRenewBook = async (issueId) => {
    try {
      const response = await apiCall(`/api/books/renew/${issueId}`, {
        method: "POST"
      })
      
      if (response.success) {
        // Refresh issued books
        const booksData = await apiCall("/api/users/issued-books")
        setIssuedBooks(booksData.issued_books || [])
        alert(response.message)
      } else {
        alert(response.message)
      }
    } catch (error) {
      alert("Error renewing book: " + error.message)
    }
  }

  const handleReturnBook = async (issueId) => {
    try {
      const response = await apiCall(`/api/books/return/${issueId}`, {
        method: "POST"
      })
      
      if (response.success) {
        // Refresh issued books and profile
        const [profileData, booksData] = await Promise.all([
          apiCall("/api/users/profile"),
          apiCall("/api/users/issued-books")
        ])
        setProfile(profileData)
        setIssuedBooks(booksData.issued_books || [])
        alert(response.message)
      } else {
        alert(response.message)
      }
    } catch (error) {
      alert("Error returning book: " + error.message)
    }
  }

  const markNotificationRead = async (notificationId) => {
    try {
      await apiCall(`/api/users/notifications/${notificationId}/read`, {
        method: "PUT"
      })
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      )
    } catch (error) {
      console.error("Error marking notification as read:", error)
    }
  }

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'overdue': return '#dc2626'
      case 'due_soon': return '#d97706'
      default: return '#059669'
    }
  }

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success': return '✅'
      case 'warning': return '⚠️'
      case 'error': return '❌'
      default: return 'ℹ️'
    }
  }

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading your library profile...</p>
      </div>
    )
  }

  return (
    <div className="user-profile">
      <h1>👤 Library Profile</h1>

      {/* Profile Overview */}
      <div className="profile-overview" style={{
        background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
        color: 'white',
        borderRadius: '1rem',
        padding: '2rem',
        marginBottom: '2rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
          <div>
            <h2 style={{ margin: '0 0 0.5rem 0', color: 'white' }}>
              {profile.first_name} {profile.last_name}
            </h2>
            <p style={{ margin: '0 0 1rem 0', opacity: 0.9 }}>
              @{profile.username} • Member since {profile.member_since}
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <p style={{ margin: '0 0 0.25rem 0', fontSize: '2rem', fontWeight: '700' }}>
              {profile.library_stats?.books_issued || 0}/{profile.library_stats?.max_books_allowed || 5}
            </p>
            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.875rem' }}>Books Issued</p>
          </div>
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '1rem',
          marginTop: '1.5rem'
        }}>
          <div style={{ 
            backgroundColor: 'rgba(255,255,255,0.2)', 
            padding: '1rem', 
            borderRadius: '0.5rem',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <AlertTriangle size={20} />
              <span style={{ fontWeight: '600' }}>Overdue Books</span>
            </div>
            <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700' }}>
              {profile.library_stats?.books_overdue || 0}
            </p>
          </div>

          <div style={{ 
            backgroundColor: 'rgba(255,255,255,0.2)', 
            padding: '1rem', 
            borderRadius: '0.5rem',
            backdropFilter: 'blur(10px)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '1.25rem' }}>💰</span>
              <span style={{ fontWeight: '600' }}>Total Fines</span>
            </div>
            <p style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700' }}>
              ₹{profile.library_stats?.total_fine || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Currently Issued Books */}
      <div className="form-section">
        <h2>
          <Book className="section-icon" /> Currently Issued Books ({issuedBooks.length})
        </h2>

        {issuedBooks.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '3rem',
            backgroundColor: '#f8fafc',
            borderRadius: '1rem',
            border: '2px dashed #e2e8f0'
          }}>
            <Book size={48} style={{ color: '#94a3b8', marginBottom: '1rem' }} />
            <h3 style={{ color: '#64748b', marginBottom: '0.5rem' }}>No books issued</h3>
            <p style={{ color: '#64748b' }}>Visit the chat or search page to issue some books!</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {issuedBooks.map((book) => (
              <div key={book.id} style={{
                background: book.urgency === 'overdue' ? 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)' : 
                          book.urgency === 'due_soon' ? 'linear-gradient(135deg, #fefce8 0%, #fef3c7 100%)' : 
                          'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
                border: `2px solid ${
                  book.urgency === 'overdue' ? '#fecaca' : 
                  book.urgency === 'due_soon' ? '#fed7aa' : '#bbf7d0'
                }`,
                borderRadius: '1rem',
                padding: '1.5rem',
                display: 'flex',
                gap: '1rem'
              }}>
                <div style={{ flexShrink: 0 }}>
                  <img 
                    src={book.book_image_url || '/placeholder-book.png'} 
                    alt={book.book_title}
                    style={{
                      width: '80px',
                      height: '120px',
                      objectFit: 'cover',
                      borderRadius: '0.5rem',
                      backgroundColor: '#f1f5f9'
                    }}
                  />
                </div>

                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '1.125rem', fontWeight: '600' }}>
                    {book.book_title}
                  </h4>
                  <p style={{ margin: '0 0 1rem 0', color: '#64748b', fontStyle: 'italic' }}>
                    by {book.book_author}
                  </p>

                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                    gap: '1rem',
                    marginBottom: '1rem'
                  }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <Calendar size={16} />
                        <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Issue Date</span>
                      </div>
                      <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748b' }}>
                        {new Date(book.issue_date).toLocaleDateString()}
                      </p>
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <Calendar size={16} />
                        <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Due Date</span>
                      </div>
                      <p style={{ 
                        margin: 0, 
                        fontSize: '0.875rem', 
                        color: getUrgencyColor(book.urgency),
                        fontWeight: '500'
                      }}>
                        {new Date(book.due_date).toLocaleDateString()} ({book.urgency_text})
                      </p>
                    </div>

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                        <RotateCcw size={16} />
                        <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Renewals</span>
                      </div>
                      <p style={{ margin: 0, fontSize: '0.875rem', color: '#64748b' }}>
                        {book.renewal_count}/2 used
                      </p>
                    </div>

                    {book.current_fine > 0 && (
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                          <AlertTriangle size={16} />
                          <span style={{ fontSize: '0.875rem', fontWeight: '500' }}>Current Fine</span>
                        </div>
                        <p style={{ margin: 0, fontSize: '0.875rem', color: '#dc2626', fontWeight: '600' }}>
                          ₹{book.current_fine}
                        </p>
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    {book.can_renew && (
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleRenewBook(book.id)}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                      >
                        <RotateCcw size={16} />
                        Renew Book
                      </button>
                    )}
                    
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleReturnBook(book.id)}
                      style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                    >
                      <Book size={16} />
                      Return Book
                    </button>

                    {!book.can_renew && (
                      <span style={{ 
                        fontSize: '0.75rem', 
                        color: '#dc2626', 
                        alignSelf: 'center',
                        fontStyle: 'italic'
                      }}>
                        {book.renewal_count >= 2 ? 'Max renewals reached' : 'Cannot renew overdue book'}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Notifications */}
      <div className="form-section">
        <h2>
          <Bell className="section-icon" /> Recent Notifications ({notifications.filter(n => !n.is_read).length} unread)
        </h2>

        {notifications.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '2rem',
            backgroundColor: '#f8fafc',
            borderRadius: '0.75rem',
            border: '1px solid #e2e8f0'
          }}>
            <Bell size={32} style={{ color: '#94a3b8', marginBottom: '1rem' }} />
            <p style={{ color: '#64748b', margin: 0 }}>No notifications yet</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
            {notifications.map((notification) => (
              <div 
                key={notification.id} 
                onClick={() => !notification.is_read && markNotificationRead(notification.id)}
                style={{
                  backgroundColor: notification.is_read ? '#f8fafc' : '#ffffff',
                  border: `1px solid ${notification.is_read ? '#e2e8f0' : '#3b82f6'}`,
                  borderRadius: '0.5rem',
                  padding: '1rem',
                  cursor: notification.is_read ? 'default' : 'pointer',
                  transition: 'all 0.2s',
                  opacity: notification.is_read ? 0.7 : 1
                }}
              >
                <div style={{ display: 'flex', alignItems: 'start', gap: '0.75rem' }}>
                  <span style={{ fontSize: '1.25rem', flexShrink: 0 }}>
                    {getNotificationIcon(notification.notification_type)}
                  </span>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ 
                      margin: '0 0 0.25rem 0', 
                      fontSize: '0.875rem', 
                      fontWeight: '600',
                      color: notification.is_read ? '#64748b' : '#1e293b'
                    }}>
                      {notification.title}
                    </h4>
                    <p style={{ 
                      margin: '0 0 0.5rem 0', 
                      fontSize: '0.8125rem', 
                      color: '#64748b',
                      lineHeight: 1.4
                    }}>
                      {notification.message}
                    </p>
                    <p style={{ 
                      margin: 0, 
                      fontSize: '0.75rem', 
                      color: '#94a3b8'
                    }}>
                      {new Date(notification.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Library Rules */}
      <div className="profile-help">
        <h3>📋 Library Rules & Information</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1rem',
          marginTop: '1rem'
        }}>
          <div>
            <h4 style={{ color: '#3b82f6', marginBottom: '0.5rem' }}>📚 Borrowing Rules</h4>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#64748b' }}>
              <li>Maximum 5 books at a time</li>
              <li>15 days borrowing period</li>
              <li>Maximum 2 renewals per book</li>
              <li>Renewal only if not overdue by more than 3 days</li>
            </ul>
          </div>
          <div>
            <h4 style={{ color: '#dc2626', marginBottom: '0.5rem' }}>💰 Fine Structure</h4>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#64748b' }}>
              <li>₹50 per day for overdue books</li>
              <li>Fine calculated from day after due date</li>
              <li>Pay fines at library counter</li>
              <li>Cannot issue new books with pending fines</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserProfile