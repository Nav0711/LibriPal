import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import ErrorBoundary from './components/common/ErrorBoundary';
import './styles/globals.css';
import './index.css';

// Import any polyfills if needed
import 'core-js/stable';
import 'regenerator-runtime/runtime';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

// Register service worker for PWA functionality (optional)
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Performance monitoring (optional)
if (process.env.NODE_ENV === 'production') {
  // You can add performance monitoring here
  // Example: import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';
}