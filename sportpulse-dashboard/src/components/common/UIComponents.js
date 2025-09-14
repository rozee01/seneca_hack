import React from 'react';

export const LoadingSpinner = ({ size = 'medium' }) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12'
  };

  return (
    <div className="flex justify-center items-center">
      <div className={`${sizeClasses[size]} border-4 border-gray-600 border-t-blue-500 rounded-full animate-spin`}></div>
    </div>
  );
};

export const ErrorMessage = ({ message, onRetry }) => (
  <div className="p-4 bg-red-900 border border-red-700 rounded-lg">
    <p className="text-red-200 mb-2">⚠️ {message}</p>
    {onRetry && (
      <button 
        onClick={onRetry}
        className="px-3 py-1 bg-red-700 hover:bg-red-600 text-white text-sm rounded transition-colors"
      >
        Retry
      </button>
    )}
  </div>
);

export const EmptyState = ({ message, icon = "📊" }) => (
  <div className="text-center py-8">
    <div className="text-4xl mb-4">{icon}</div>
    <p className="text-gray-400">{message}</p>
  </div>
);