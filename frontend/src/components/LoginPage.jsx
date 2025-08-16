import React from 'react';
import { SignIn } from '@clerk/clerk-react';
import { Book, MessageCircle, Search, Bell } from 'lucide-react';

const LoginPage = () => {
  return (
    <div className="login-page">
      <div className="login-content">
        <div className="login-hero">
          <div className="hero-header">
            <Book className="hero-icon" />
            <h1>LibriPal</h1>
            <p>Your AI-Powered Library Assistant</p>
          </div>

          <div className="features-grid">
            <div className="feature">
              <Search className="feature-icon" />
              <h3>Smart Search</h3>
              <p>Find books using natural language queries</p>
            </div>
            
            <div className="feature">
              <MessageCircle className="feature-icon" />
              <h3>Chat Assistant</h3>
              <p>Get help through friendly conversation</p>
            </div>
            
            <div className="feature">
              <Bell className="feature-icon" />
              <h3>Smart Reminders</h3>
              <p>Never miss a due date with AI-powered notifications</p>
            </div>
            
            <div className="feature">
              <Book className="feature-icon" />
              <h3>Personalized Recommendations</h3>
              <p>Discover books tailored to your interests</p>
            </div>
          </div>
        </div>

        <div className="login-form-container">
          <SignIn 
            appearance={{
              elements: {
                formButtonPrimary: 'btn btn-primary',
                card: 'login-card'
              }
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default LoginPage;