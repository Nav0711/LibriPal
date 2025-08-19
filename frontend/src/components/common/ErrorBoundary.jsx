"use client"

import React from "react"
import { AlertTriangle, RefreshCw, Home } from "lucide-react"

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true }
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo,
    })

    // Log error to console in development
    if (process.env.NODE_ENV === "development") {
      console.error("ErrorBoundary caught an error:", error, errorInfo)
    }

    // In production, you might want to log to an error reporting service
    // logErrorToService(error, errorInfo);
  }

  handleRefresh = () => {
    window.location.reload()
  }

  handleGoHome = () => {
    window.location.href = "/"
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
            <div className="flex justify-center mb-4">
              <AlertTriangle className="h-12 w-12 text-red-500" />
            </div>

            <h1 className="text-xl font-semibold text-gray-900 mb-2">Oops! Something went wrong</h1>

            <p className="text-gray-600 mb-6">
              We're sorry, but something unexpected happened. Our team has been notified and is working on a fix.
            </p>

            {process.env.NODE_ENV === "development" && (
              <div className="mb-6 p-4 bg-gray-50 rounded-lg text-left">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Error Details (Development Mode):</h3>
                <pre className="text-xs text-red-600 whitespace-pre-wrap overflow-auto max-h-32">
                  {this.state.error && this.state.error.toString()}
                  {this.state.errorInfo.componentStack}
                </pre>
              </div>
            )}

            <div className="flex gap-3 justify-center">
              <button onClick={this.handleRefresh} className="btn btn-primary flex items-center gap-2">
                <RefreshCw className="h-4 w-4" />
                Try Again
              </button>

              <button onClick={this.handleGoHome} className="btn btn-outline flex items-center gap-2">
                <Home className="h-4 w-4" />
                Go Home
              </button>
            </div>

            <div className="mt-6 pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                If this problem persists, please{" "}
                <a href="mailto:support@libripal.com" className="text-blue-600 hover:text-blue-800">
                  contact support
                </a>
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Functional Error Fallback Component
export const ErrorFallback = ({
  error,
  resetErrorBoundary,
  title = "Something went wrong",
  description = "An unexpected error occurred. Please try again.",
}) => (
  <div className="flex flex-col items-center justify-center p-8 text-center">
    <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
    <h2 className="text-lg font-semibold text-gray-900 mb-2">{title}</h2>
    <p className="text-gray-600 mb-4">{description}</p>

    {process.env.NODE_ENV === "development" && error && (
      <details className="mb-4 max-w-lg">
        <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">Show error details</summary>
        <pre className="mt-2 text-xs text-red-600 whitespace-pre-wrap text-left bg-gray-50 p-2 rounded overflow-auto max-h-32">
          {error.toString()}
        </pre>
      </details>
    )}

    <button onClick={resetErrorBoundary} className="btn btn-primary flex items-center gap-2">
      <RefreshCw className="h-4 w-4" />
      Try again
    </button>
  </div>
)

// Hook for error handling in functional components
export const useErrorHandler = () => {
  return (error, errorInfo) => {
    console.error("Error caught by error handler:", error, errorInfo)

    // You can also trigger error reporting here
    // reportError(error, errorInfo);
  }
}

export default ErrorBoundary
