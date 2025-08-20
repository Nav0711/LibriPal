import React, { createContext, useContext, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
// import Dashboard from './components/Dashboard';
import ChatInterface from './components/ChatInterface';
import BookSearch from './components/BookSearch';
// import UserProfile from './components/UserProfile';
import Navigation from './components/Navigation';
import LoginPage from './components/LoginPage';
import './App.css';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

function AuthProvider({ children }) {
  const [user, setUser] = useState({
    username: "Enthusiast-AD",
    email: "enthusiast-ad@libripal.com",
    first_name: "Enthusiast",
    last_name: "AD"
  });
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Skip auth for now

  const apiCall = async (endpoint, options = {}) => {
    const url = `http://localhost:8000${endpoint}`;
    console.log('Making API call to:', url, options);
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      
      if (!response.ok) {
        throw new Error(`API call failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('API response:', data);
      return data;
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  };

  const value = {
    user,
    isAuthenticated,
    apiCall,
    login: () => setIsAuthenticated(true),
    logout: () => setIsAuthenticated(false)
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

function AppContent() {
  const { isAuthenticated, apiCall } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  return (
    <Router
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/chat" element={<ChatInterface apiCall={apiCall} />} />
            <Route path="/search" element={<BookSearch apiCall={apiCall} />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;