import React from 'react';

const LoadingSpinner = ({ 
  size = 'medium', 
  color = '#3b82f6', 
  text = 'Loading...', 
  fullPage = false 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8', 
    large: 'w-12 h-12'
  };

  const containerClasses = fullPage 
    ? 'fixed inset-0 flex items-center justify-center bg-white bg-opacity-75 z-50'
    : 'flex items-center justify-center p-4';

  return (
    <div className={containerClasses}>
      <div className="flex flex-col items-center space-y-2">
        <div
          className={`${sizeClasses[size]} border-4 border-gray-200 border-t-current rounded-full animate-spin`}
          style={{ borderTopColor: color }}
        ></div>
        {text && (
          <p className="text-sm text-gray-600 font-medium">{text}</p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;

export const InlineSpinner = ({ size = 'small', className = '' }) => (
  <div className={`inline-flex items-center ${className}`}>
    <div className={`${size === 'small' ? 'w-4 h-4' : 'w-6 h-6'} border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin`}></div>
  </div>
);

export const ButtonSpinner = () => (
  <div className="inline-flex items-center">
    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
    Loading...
  </div>
);

export const SkeletonLoader = ({ lines = 3, className = '' }) => (
  <div className={`animate-pulse ${className}`}>
    {Array.from({ length: lines }).map((_, index) => (
      <div
        key={index}
        className={`bg-gray-200 rounded h-4 mb-2 ${
          index === lines - 1 ? 'w-3/4' : 'w-full'
        }`}
      ></div>
    ))}
  </div>
);

export const CardSkeleton = () => (
  <div className="animate-pulse">
    <div className="bg-gray-200 rounded-lg h-48 mb-4"></div>
    <div className="bg-gray-200 rounded h-4 mb-2"></div>
    <div className="bg-gray-200 rounded h-4 w-3/4 mb-2"></div>
    <div className="bg-gray-200 rounded h-4 w-1/2"></div>
  </div>
);