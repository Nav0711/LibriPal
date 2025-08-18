import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Book, Clock, Star } from 'lucide-react';

const ChatInterface = ({ apiCall }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello Enthusiast-AD! 👋 I'm LibriPal, your AI-powered library assistant. I'm here to help you find books, check your account, and answer any library questions you might have. What would you like to explore today?",
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
      console.log('🤖 Sending to Gemini AI:', currentMessage);
      
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

      console.log('🧠 Gemini AI response:', response);

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
        content: 'I apologize, but I\'m having trouble connecting to my AI brain right now. Please try again in a moment, or feel free to ask me something else!',
        suggestions: ['Try again', 'Check library hours', 'Search for books'],
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
              📚 Found {data.length} book{data.length !== 1 ? 's' : ''}:
            </h4>
            {data.map(book => (
              <div key={book.id} className="book-result-card" style={{
                background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                border: '1px solid #e2e8f0',
                borderRadius: '0.75rem',
                padding: '1rem',
                marginBottom: '0.75rem',
                transition: 'transform 0.2s',
                cursor: 'pointer'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                  <h5 style={{ margin: '0', fontSize: '0.875rem', fontWeight: '600', color: '#1e293b' }}>
                    {book.title}
                  </h5>
                  <span style={{
                    backgroundColor: book.available_copies > 0 ? '#dcfce7' : '#fee2e2',
                    color: book.available_copies > 0 ? '#166534' : '#991b1b',
                    padding: '0.125rem 0.5rem',
                    borderRadius: '1rem',
                    fontSize: '0.75rem',
                    fontWeight: '500'
                  }}>
                    {book.available_copies > 0 ? '✅ Available' : '❌ Unavailable'}
                  </span>
                </div>
                
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem', color: '#64748b', fontStyle: 'italic' }}>
                  by {book.author}
                </p>
                
                {book.ai_summary && (
                  <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.75rem', color: '#475569', lineHeight: '1.4' }}>
                    {book.ai_summary}
                  </p>
                )}
                
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      📖 {book.available_copies}/{book.total_copies} copies
                    </span>
                    {book.genre && (
                      <span style={{
                        backgroundColor: '#eff6ff',
                        color: '#3b82f6',
                        padding: '0.125rem 0.375rem',
                        borderRadius: '0.25rem',
                        fontSize: '0.625rem',
                        fontWeight: '500'
                      }}>
                        {book.genre}
                      </span>
                    )}
                  </div>
                  
                  {book.available_copies > 0 && (
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
                        transition: 'background-color 0.2s'
                      }}
                      onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
                      onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
                    >
                      📖 Borrow
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Library Hours */}
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

  const smartSuggestions = [
    "Find books about machine learning",
    "What are the library hours?",
    "Show me popular programming books",
    "How do I renew my books?",
    "Recommend books for data science",
    "Check my account status"
  ];

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bot className="chat-icon" />
          <div>
            <h2 style={{ margin: 0, fontSize: '1.125rem' }}>LibriPal AI Assistant</h2>
            <p style={{ margin: 0, fontSize: '0.75rem', color: '#64748b' }}>
              Powered by Gemini AI • Ready to help
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
                🧠 Thinking with Gemini AI...
              </p>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="quick-actions">
        <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', color: '#64748b', fontWeight: '500' }}>
          🚀 Quick suggestions:
        </p>
        <div className="quick-buttons">
          {smartSuggestions.map((action, index) => (
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
          placeholder="Ask me anything about the library... (powered by Gemini AI)"
          className="chat-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={isLoading || !inputMessage.trim()}
          title="Send message to Gemini AI"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;