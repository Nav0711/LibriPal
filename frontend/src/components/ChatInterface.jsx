import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Star, Calendar, AlertTriangle, RotateCcw } from 'lucide-react';

const ChatInterface = ({ apiCall }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello Enthusiast-AD! 👋 I'm LibriPal with complete book management. I can help you search, issue, renew books, check fines, and manage your library account. What would you like to do today?",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiCall('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ 
          message: currentMessage,
          context: { user: "Enthusiast-AD", timestamp: new Date().toISOString() }
        })
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.message,
        data: response.data,
        responseType: response.type,
        suggestions: response.suggestions,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('❌ Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'I\'m having trouble right now. Please try again!',
        suggestions: ['Try again', 'Check my books', 'Search books'],
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action) => {
    setInputMessage(action);
  };

  const handleIssueBook = async (book) => {
    try {
      const response = await apiCall('/api/books/issue', {
        method: 'POST',
        body: JSON.stringify({
          book_id: book.id,
          book_title: book.title,
          book_author: book.author,
          book_image_url: book.image_url,
          book_price: book.price
        })
      });
      
      const confirmationMessage = {
        id: Date.now(),
        type: 'bot',
        content: `${response.success ? '✅' : '❌'} ${response.message}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, confirmationMessage]);
    } catch (error) {
      console.error('Issue error:', error);
    }
  };

  const handleRenewBook = async (issueId) => {
    try {
      const response = await apiCall(`/api/books/renew/${issueId}`, {
        method: 'POST'
      });
      
      const confirmationMessage = {
        id: Date.now(),
        type: 'bot',
        content: `${response.success ? '✅' : '❌'} ${response.message}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, confirmationMessage]);
    } catch (error) {
      console.error('Renewal error:', error);
    }
  };

  const renderBookCard = (book) => (
    <div key={book.id} className="book-result-card" style={{
      background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
      border: '1px solid #e2e8f0',
      borderRadius: '1rem',
      padding: '1rem',
      marginBottom: '1rem',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      display: 'flex',
      gap: '1rem'
    }}>
      <div style={{ flexShrink: 0 }}>
        <img 
          src={book.image_url || '/placeholder-book.png'} 
          alt={book.title}
          style={{
            width: '80px',
            height: '120px',
            objectFit: 'cover',
            borderRadius: '0.5rem',
            backgroundColor: '#f1f5f9'
          }}
          onError={(e) => {
            e.target.src = `https://via.placeholder.com/80x120/3b82f6/ffffff?text=${encodeURIComponent(book.title.substring(0, 10))}`;
          }}
        />
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
          <h5 style={{ 
            margin: '0', 
            fontSize: '0.9rem', 
            fontWeight: '600', 
            color: '#1e293b',
            lineHeight: 1.3
          }}>
            {book.title}
          </h5>
          <span style={{
            backgroundColor: book.can_issue ? '#dcfce7' : '#fee2e2',
            color: book.can_issue ? '#166534' : '#991b1b',
            padding: '0.125rem 0.5rem',
            borderRadius: '1rem',
            fontSize: '0.7rem',
            fontWeight: '500',
            whiteSpace: 'nowrap'
          }}>
            {book.can_issue ? '✅ Can Issue' : '❌ Limit Reached'}
          </span>
        </div>
        
        <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic' }}>
          by {book.author}
        </p>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.75rem' }}>
          <span style={{ fontSize: '0.8rem', fontWeight: '600', color: '#059669' }}>
            {book.price}
          </span>
          <span style={{ fontSize: '0.7rem', color: '#64748b' }}>
            {book.source}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {book.can_issue ? (
            <button
              onClick={() => handleIssueBook(book)}
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                padding: '0.375rem 0.75rem',
                borderRadius: '0.375rem',
                fontSize: '0.75rem',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              📖 Issue Book
            </button>
          ) : (
            <span style={{ fontSize: '0.75rem', color: '#ef4444' }}>
              Max 5 books limit reached
            </span>
          )}
        </div>
      </div>
    </div>
  );

  const renderIssuedBookCard = (book) => (
    <div key={book.id} className="issued-book-card" style={{
      background: book.urgency === 'overdue' ? 'linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)' : 
                 book.urgency === 'due_soon' ? 'linear-gradient(135deg, #fefce8 0%, #fef3c7 100%)' : 
                 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
      border: `1px solid ${book.urgency === 'overdue' ? '#fecaca' : book.urgency === 'due_soon' ? '#fed7aa' : '#bbf7d0'}`,
      borderRadius: '1rem',
      padding: '1rem',
      marginBottom: '1rem',
      display: 'flex',
      gap: '1rem'
    }}>
      <div style={{ flexShrink: 0 }}>
        <img 
          src={book.book_image_url || '/placeholder-book.png'} 
          alt={book.book_title}
          style={{
            width: '60px',
            height: '90px',
            objectFit: 'cover',
            borderRadius: '0.5rem'
          }}
        />
      </div>

      <div style={{ flex: 1 }}>
        <h5 style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', fontWeight: '600' }}>
          {book.book_title}
        </h5>
        <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem', color: '#64748b' }}>
          by {book.book_author}
        </p>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Calendar size={12} />
            <span style={{ fontSize: '0.75rem' }}>
              Due: {new Date(book.due_date).toLocaleDateString()}
            </span>
          </div>
          <span style={{ 
            fontSize: '0.75rem', 
            color: book.urgency === 'overdue' ? '#dc2626' : book.urgency === 'due_soon' ? '#d97706' : '#059669',
            fontWeight: '500'
          }}>
            {book.urgency_text}
          </span>
        </div>

        {book.current_fine > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', marginBottom: '0.5rem' }}>
            <AlertTriangle size={12} style={{ color: '#dc2626' }} />
            <span style={{ fontSize: '0.75rem', color: '#dc2626', fontWeight: '500' }}>
              Fine: ₹{book.current_fine}
            </span>
          </div>
        )}

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          {book.can_renew && (
            <button
              onClick={() => handleRenewBook(book.id)}
              style={{
                backgroundColor: '#059669',
                color: 'white',
                border: 'none',
                padding: '0.25rem 0.5rem',
                borderRadius: '0.25rem',
                fontSize: '0.75rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem'
              }}
            >
              <RotateCcw size={12} />
              Renew
            </button>
          )}
          <span style={{ fontSize: '0.7rem', color: '#64748b' }}>
            Renewals: {book.renewal_count}/2
          </span>
        </div>
      </div>
    </div>
  );

  const renderBotMessage = (message) => {
    const { content, data, responseType, suggestions } = message;

    return (
      <div className="bot-message-content">
        <div className="message-text" style={{ whiteSpace: 'pre-line', marginBottom: '1rem' }}>
          {content}
        </div>
        
        {/* Book Search Results */}
        {responseType === 'book_search' && data && data.length > 0 && (
          <div className="search-results" style={{ marginTop: '1rem' }}>
            {data.map(renderBookCard)}
          </div>
        )}

        {/* Issued Books */}
        {responseType === 'issued_books' && data && data.length > 0 && (
          <div className="issued-books" style={{ marginTop: '1rem' }}>
            {data.map(renderIssuedBookCard)}
          </div>
        )}

        {/* Fines Display */}
        {responseType === 'fines' && data && (
          <div className="fines-display" style={{ marginTop: '1rem' }}>
            {data.length > 0 ? (
              data.map(renderIssuedBookCard)
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '2rem', 
                backgroundColor: '#f0fdf4', 
                borderRadius: '0.5rem',
                border: '1px solid #bbf7d0'
              }}>
                <span style={{ fontSize: '2rem' }}>🎉</span>
                <p style={{ margin: '0.5rem 0 0 0', color: '#059669', fontWeight: '500' }}>
                  No outstanding fines! You're all clear.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Library Hours */}
        {responseType === 'library_info' && data && data.hours && (
          <div className="library-info" style={{ 
            marginTop: '1rem',
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '0.5rem',
            padding: '1rem'
          }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: '#1e293b', fontSize: '0.875rem' }}>
              📋 Library Rules & Hours
            </h4>
            <div style={{ marginBottom: '1rem' }}>
              <p style={{ margin: '0.25rem 0', fontSize: '0.75rem' }}>
                📚 Max books: {data.max_books} | 📅 Borrow period: {data.max_borrow_days} days
              </p>
              <p style={{ margin: '0.25rem 0', fontSize: '0.75rem' }}>
                💰 Fine: {data.fine_per_day}/day after due date | 🔄 Max renewals: {data.max_renewals}
              </p>
            </div>
            {Object.entries(data.hours).map(([day, hours]) => (
              <div key={day} style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                padding: '0.25rem 0',
                fontSize: '0.75rem'
              }}>
                <span style={{ fontWeight: '500', textTransform: 'capitalize' }}>{day}:</span>
                <span>{hours}</span>
              </div>
            ))}
          </div>
        )}

        {/* AI Suggestions */}
        {suggestions && suggestions.length > 0 && (
          <div className="ai-suggestions" style={{ marginTop: '1rem' }}>
            <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem', color: '#64748b', fontWeight: '500' }}>
              💡 You might also want to:
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(suggestion)}
                  style={{
                    backgroundColor: 'white',
                    border: '1px solid #e2e8f0',
                    padding: '0.375rem 0.75rem',
                    borderRadius: '1rem',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    color: '#374151'
                  }}
                  onMouseOver={(e) => {
                    e.target.style.backgroundColor = '#3b82f6';
                    e.target.style.color = 'white';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = 'white';
                    e.target.style.color = '#374151';
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const libraryManagementSuggestions = [
    "Show my issued books",
    "Check my fines",
    "Find programming books",
    "Search for fiction novels",
    "What are the library rules?",
    "How do I renew books?"
  ];

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bot className="chat-icon" />
          <div>
            <h2 style={{ margin: 0, fontSize: '1.125rem' }}>LibriPal Library Assistant</h2>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#64748b' }}>
              Complete Book Management • Issue • Return • Renew • Fines in ₹
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <div style={{
            width: '8px',
            height: '8px',
            backgroundColor: '#10b981',
            borderRadius: '50%'
          }}></div>
          <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: '500' }}>Online</span>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className="message-avatar">
              {message.type === 'bot' ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className="message-content">
              {message.type === 'bot' ? renderBotMessage(message) : (
                <p>{message.content}</p>
              )}
              <span className="message-time">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="message-avatar">
              <Bot size={20} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.75rem', color: '#64748b' }}>
                🧠 Processing your request...
              </p>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-actions">
        <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', color: '#64748b', fontWeight: '500' }}>
          🚀 Quick actions:
        </p>
        <div className="quick-buttons">
          {libraryManagementSuggestions.map((action, index) => (
            <button
              key={index}
              className="quick-action-btn"
              onClick={() => handleQuickAction(action)}
            >              {action}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask me anything... Issue books, check fines, renew books, or search our library!"
          className="chat-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={isLoading || !inputMessage.trim()}
          title="Send to LibriPal AI"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;