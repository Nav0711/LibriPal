import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Book, Calendar, AlertCircle } from 'lucide-react';

const ChatInterface = ({ apiCall }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hi! I'm LibriPal, your AI library assistant. How can I help you today?",
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
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiCall('/chat', {
        method: 'POST',
        body: JSON.stringify({ message: inputMessage })
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.message,
        data: response.data,
        responseType: response.type,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReserveBook = async (bookId) => {
    try {
      const response = await apiCall('/reserve', {
        method: 'POST',
        body: JSON.stringify({ book_id: bookId })
      });
      
      const confirmationMessage = {
        id: Date.now(),
        type: 'bot',
        content: response.message,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, confirmationMessage]);
    } catch (error) {
      alert('Error reserving book: ' + error.message);
    }
  };

  const renderBotMessage = (message) => {
    const { content, data, responseType } = message;

    return (
      <div className="bot-message-content">
        <p>{content}</p>
        
        {responseType === 'book_search' && data && data.length > 0 && (
          <div className="search-results">
            {data.map(book => (
              <div key={book.id} className="search-result-card">
                <img 
                  src={book.cover_image_url || '/placeholder-book.png'} 
                  alt={book.title}
                  className="result-book-cover"
                />
                <div className="result-book-info">
                  <h4>{book.title}</h4>
                  <p>by {book.author}</p>
                  {book.ai_summary && <p className="book-summary">{book.ai_summary}</p>}
                  <p>Available: {book.available_copies}/{book.total_copies}</p>
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => handleReserveBook(book.id)}
                    disabled={book.available_copies === 0}
                  >
                    {book.available_copies > 0 ? 'Borrow' : 'Reserve'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {responseType === 'borrowed_books' && data && data.length > 0 && (
          <div className="borrowed-books-list">
            {data.map(book => (
              <div key={book.id} className="borrowed-book-card">
                <div className="book-info">
                  <h4>{book.title}</h4>
                  <p>Due: {new Date(book.due_date).toLocaleDateString()}</p>
                  <span className={`urgency-badge ${book.urgency}`}>
                    {book.urgency === 'overdue' ? '🚨 Overdue' : 
                     book.urgency === 'due_soon' ? '⚠️ Due Soon' : '✅ Normal'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        {responseType === 'recommendations' && data && data.length > 0 && (
          <div className="recommendations-list">
            {data.map(book => (
              <div key={book.id} className="recommendation-card">
                <img 
                  src={book.cover_image_url || '/placeholder-book.png'} 
                  alt={book.title}
                  className="rec-book-cover"
                />
                <div className="rec-book-info">
                  <h4>{book.title}</h4>
                  <p>by {book.author}</p>
                  <button 
                    className="btn btn-outline btn-sm"
                    onClick={() => handleReserveBook(book.id)}
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {responseType === 'library_info' && data && (
          <div className="library-hours">
            {Object.entries(data).map(([day, hours]) => (
              <div key={day} className="hours-row">
                <span className="day">{day.charAt(0).toUpperCase() + day.slice(1)}:</span>
                <span className="hours">{hours}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const quickActions = [
    "Search for books on machine learning",
    "Show my borrowed books",
    "Check my due dates",
    "Recommend similar books",
    "What are the library hours?",
    "Show my fines"
  ];

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <Bot className="chat-icon" />
        <h2>LibriPal Assistant</h2>
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
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <p>Quick actions:</p>
        <div className="quick-buttons">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="quick-action-btn"
              onClick={() => setInputMessage(action)}
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
          placeholder="Ask me anything about the library..."
          className="chat-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={isLoading || !inputMessage.trim()}
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInterface;