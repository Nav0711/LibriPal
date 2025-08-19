import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Star, ShoppingCart } from 'lucide-react';

const ChatInterface = ({ apiCall }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello Enthusiast-AD! 👋 I'm LibriPal with enhanced memory and access to 100k+ books. I remember our previous conversations and can help you find books from our extensive database. What would you like to explore today?",
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
      console.log('🧠 Sending to Context-Aware Gemini:', currentMessage);
      
      const response = await apiCall('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ 
          message: currentMessage,
          context: {
            user: "Enthusiast-AD",
            timestamp: new Date().toISOString()
          }
        })
      });

      console.log('🤖 Context-Aware Response:', response);

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
        content: 'I\'m having trouble right now, but I remember our conversation! Please try again and I\'ll pick up where we left off.',
        suggestions: ['Try again', 'Search for books', 'Continue our conversation'],
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

  const handleBorrowBook = async (bookId) => {
    try {
      const response = await apiCall('/api/books/borrow', {
        method: 'POST',
        body: JSON.stringify({ book_id: bookId })
      });
      
      const confirmationMessage = {
        id: Date.now(),
        type: 'bot',
        content: `✅ ${response.message}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, confirmationMessage]);
    } catch (error) {
      console.error('Borrow error:', error);
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
      transition: 'transform 0.2s',
      display: 'flex',
      gap: '1rem'
    }}>
      {/* Book Image */}
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

      {/* Book Details */}
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
            backgroundColor: book.available_copies > 0 ? '#dcfce7' : '#fee2e2',
            color: book.available_copies > 0 ? '#166534' : '#991b1b',
            padding: '0.125rem 0.5rem',
            borderRadius: '1rem',
            fontSize: '0.7rem',
            fontWeight: '500',
            whiteSpace: 'nowrap'
          }}>
            {book.available_copies > 0 ? '✅ Available' : '❌ Unavailable'}
          </span>
        </div>
        
        <p style={{ 
          margin: '0 0 0.5rem 0', 
          fontSize: '0.75rem', 
          color: '#64748b', 
          fontStyle: 'italic' 
        }}>
          by {book.author}
        </p>

        {/* Rating and Price */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
          {book.rating && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Star size={12} style={{ color: '#fbbf24', fill: 'currentColor' }} />
              <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{book.rating}</span>
            </div>
          )}
          {book.price && (
            <span style={{ 
              fontSize: '0.8rem', 
              fontWeight: '600', 
              color: '#059669' 
            }}>
              {book.price}
            </span>
          )}
        </div>

        {/* Categories */}
        {book.categories && book.categories.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginBottom: '0.75rem' }}>
            {book.categories.slice(0, 2).map((category, index) => (
              <span key={index} style={{
                backgroundColor: '#eff6ff',
                color: '#3b82f6',
                padding: '0.125rem 0.375rem',
                borderRadius: '0.25rem',
                fontSize: '0.625rem',
                fontWeight: '500'
              }}>
                {category}
              </span>
            ))}
          </div>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {book.available_copies > 0 ? (
            <button
              onClick={() => handleBorrowBook(book.id)}
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                padding: '0.375rem 0.75rem',
                borderRadius: '0.375rem',
                fontSize: '0.75rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
            >
              📖 Borrow
            </button>
          ) : (
            <button
              style={{
                backgroundColor: '#f59e0b',
                color: 'white',
                border: 'none',
                padding: '0.375rem 0.75rem',
                borderRadius: '0.375rem',
                fontSize: '0.75rem',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              📋 Reserve
            </button>
          )}
          
          <button
            style={{
              backgroundColor: 'transparent',
              color: '#64748b',
              border: '1px solid #e2e8f0',
              padding: '0.375rem 0.5rem',
              borderRadius: '0.375rem',
              fontSize: '0.75rem',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              e.target.style.borderColor = '#3b82f6';
              e.target.style.color = '#3b82f6';
            }}
            onMouseOut={(e) => {
              e.target.style.borderColor = '#e2e8f0';
              e.target.style.color = '#64748b';
            }}
          >
            ℹ️ Details
          </button>
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
            <h4 style={{ margin: '0 0 1rem 0', color: '#3b82f6', fontSize: '0.875rem' }}>
              📚 Found {data.length} book{data.length !== 1 ? 's' : ''} from our database:
            </h4>
            {data.map(renderBookCard)}
          </div>
        )}

        {/* Library Hours (existing code) */}
        {responseType === 'library_info' && data && (
          <div className="library-hours" style={{ 
            marginTop: '1rem',
            backgroundColor: '#f8fafc',
            border: '1px solid #e2e8f0',
            borderRadius: '0.5rem',
            padding: '1rem'
          }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: '#1e293b', fontSize: '0.875rem' }}>
              🕒 Library Hours
            </h4>
            {Object.entries(data).map(([day, hours]) => (
              <div key={day} style={{ 
                display: 'flex', 
                justifyContent: 'space-between',
                padding: '0.25rem 0',
                borderBottom: day !== 'sunday' ? '1px solid #f1f5f9' : 'none'
              }}>
                <span style={{ fontWeight: '500', textTransform: 'capitalize', color: '#374151' }}>
                  {day}:
                </span>
                <span style={{ color: '#64748b' }}>{hours}</span>
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
                    e.target.style.borderColor = '#3b82f6';
                  }}
                  onMouseOut={(e) => {
                    e.target.style.backgroundColor = 'white';
                    e.target.style.color = '#374151';
                    e.target.style.borderColor = '#e2e8f0';
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

  const contextAwareSuggestions = [
    "Find programming books for beginners",
    "Show me highly rated fiction books",
    "Search for data science textbooks",
    "What are the latest bestsellers?",
    "Find books similar to what we discussed before",
    "Show me books in computer science category"
  ];

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bot className="chat-icon" />
          <div>
            <h2 style={{ margin: 0, fontSize: '1.125rem' }}>LibriPal AI Assistant</h2>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#64748b' }}>
              Context-Aware Gemini 1.5 Flash • 100k+ Books • Memory Enabled
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
                🧠 Analyzing with context-aware Gemini...
              </p>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-actions">
        <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', color: '#64748b', fontWeight: '500' }}>
          🚀 Context-aware suggestions:
        </p>
        <div className="quick-buttons">
          {contextAwareSuggestions.map((action, index) => (
            <button
              key={index}
              className="quick-action-btn"
              onClick={() => handleQuickAction(action)}
            >
              {action}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask me anything... I remember our conversation and can search 100k+ books!"
          className="chat-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={isLoading || !inputMessage.trim()}
          title="Send to Context-Aware Gemini AI"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;