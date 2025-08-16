import React, { useState, useEffect } from 'react';
import { ClerkProvider, SignedIn, SignedOut, useAuth, useUser } from '@clerk/clerk-react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import BookSearch from './components/BookSearch';
import UserProfile from './components/UserProfile';
import Navigation from './components/Navigation';
import LoginPage from './components/LoginPage';
import './App.css';

const clerkPublishableKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

function AppContent() {
  const { getToken } = useAuth();
  const { user } = useUser();
  const [apiToken, setApiToken] = useState(null);

  useEffect(() => {
    const setupToken = async () => {
      if (user) {
        const token = await getToken();
        setApiToken(token);
      }
    };
    setupToken();
  }, [user, getToken]);

  // API helper function
  const apiCall = async (endpoint, options = {}) => {
    const response = await fetch(`http://localhost:8000${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiToken}`,
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      throw new Error(`API call failed: ${response.statusText}`);
    }
    
    return response.json();
  };

  return (
    <Router>
      <div className="app">
        <SignedOut>
          <LoginPage />
        </SignedOut>
        
        <SignedIn>
          <Navigation />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard apiCall={apiCall} />} />
              <Route path="/chat" element={<ChatInterface apiCall={apiCall} />} />
              <Route path="/search" element={<BookSearch apiCall={apiCall} />} />
              <Route path="/profile" element={<UserProfile apiCall={apiCall} />} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </SignedIn>
      </div>
    </Router>
  );
}

function App() {
  return (
    <ClerkProvider publishableKey={clerkPublishableKey}>
      <AppContent />
    </ClerkProvider>
  );
}

export default App;