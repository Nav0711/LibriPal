import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { UserButton } from '@clerk/clerk-react';
import { Home, MessageCircle, Search, User, Book } from 'lucide-react';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/chat', icon: MessageCircle, label: 'Chat Assistant' },
    { path: '/search', icon: Search, label: 'Search Books' },
    { path: '/profile', icon: User, label: 'Profile' }
  ];

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <Book className="brand-icon" />
        <span className="brand-text">LibriPal</span>
      </div>

      <div className="nav-items">
        {navItems.map(item => {
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>

      <div className="nav-user">
        <UserButton afterSignOutUrl="/" />
      </div>
    </nav>
  );
};

export default Navigation;