"use client"

import { useState } from "react"
import { Star, Calendar, ExternalLink } from "lucide-react"
import { formatDate, truncateText, getUrgencyColor, getUrgencyLabel } from "../../utils/helpers"

const BookCard = ({
  book,
  onBorrow,
  onReserve,
  onRenew,
  onViewDetails,
  showActions = true,
  variant = "default", // default, borrowed, search
  loading = false,
}) => {
  const [imageError, setImageError] = useState(false)
  const [actionLoading, setActionLoading] = useState(false)

  const handleAction = async (action, ...args) => {
    setActionLoading(true)
    try {
      await action(...args)
    } catch (error) {
      console.error("Action failed:", error)
    } finally {
      setActionLoading(false)
    }
  }

  const getPlaceholderImage = () => {
    const encodedTitle = encodeURIComponent(book.title || "Book")
    return `https://via.placeholder.com/300x450/3b82f6/ffffff?text=${encodedTitle}`
  }

  const renderBorrowedVariant = () => (
    <div className={`book-card borrowed ${book.urgency}`}>
      <div className="flex gap-4">
        <img
          src={imageError ? getPlaceholderImage() : book.cover_image_url || getPlaceholderImage()}
          alt={book.title || book.book_title}
          className="book-cover w-20 h-28 object-cover rounded"
          onError={() => setImageError(true)}
        />
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-1">{book.title || book.book_title}</h4>
          <p className="text-gray-600 text-sm mb-2">by {book.author || book.book_author}</p>

          <div className="flex items-center gap-2 mb-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Due: {formatDate(book.due_date)}</span>
          </div>

          <div className="flex items-center gap-2 mb-3">
            <span
              className="urgency-badge text-xs px-2 py-1 rounded-full font-medium"
              style={{
                backgroundColor: `${getUrgencyColor(book.urgency)}20`,
                color: getUrgencyColor(book.urgency),
              }}
            >
              {getUrgencyLabel(book.urgency)}
            </span>
            {book.renewal_count > 0 && <span className="text-xs text-gray-500">Renewed: {book.renewal_count}/2</span>}
          </div>

          {showActions && (
            <div className="flex gap-2">
              {book.renewal_count < 2 && (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => handleAction(onRenew, book.id)}
                  disabled={actionLoading}
                >
                  {actionLoading ? "Renewing..." : "Renew"}
                </button>
              )}
              <button className="btn btn-outline btn-sm" onClick={() => onViewDetails && onViewDetails(book)}>
                Details
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  const renderSearchVariant = () => (
    <div className="book-card search-result">
      <div className="flex gap-4">
        <img
          src={imageError ? getPlaceholderImage() : book.cover_image_url || getPlaceholderImage()}
          alt={book.title}
          className="book-cover w-16 h-24 object-cover rounded"
          onError={() => setImageError(true)}
        />
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-1">{book.title}</h4>
          <p className="text-gray-600 text-sm mb-2">by {book.author}</p>

          {book.ai_summary && (
            <p className="text-gray-700 text-sm mb-2 leading-relaxed">{truncateText(book.ai_summary, 120)}</p>
          )}

          <div className="flex items-center gap-4 mb-3 text-xs text-gray-500">
            {book.genre && <span className="genre-tag bg-blue-50 text-blue-700 px-2 py-1 rounded">{book.genre}</span>}
            {book.publication_year && (
              <span className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {book.publication_year}
              </span>
            )}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span
                className={`availability-badge text-xs px-2 py-1 rounded-full ${
                  book.available_copies > 0 ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"
                }`}
              >
                {book.available_copies > 0 ? `${book.available_copies} available` : "Not available"}
              </span>
            </div>

            {showActions && (
              <button
                className={`btn btn-sm ${book.available_copies > 0 ? "btn-primary" : "btn-secondary"}`}
                onClick={() => handleAction(book.available_copies > 0 ? onBorrow : onReserve, book.id)}
                disabled={actionLoading}
              >
                {actionLoading ? "Processing..." : book.available_copies > 0 ? "📖 Borrow" : "⏳ Reserve"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )

  const renderDefaultVariant = () => (
    <div className="book-card default">
      <div className="relative">
        <img
          src={imageError ? getPlaceholderImage() : book.cover_image_url || getPlaceholderImage()}
          alt={book.title}
          className="book-cover w-full h-64 object-cover rounded-lg mb-4"
          onError={() => setImageError(true)}
        />

        {book.available_copies === 0 && (
          <div className="absolute top-2 right-2">
            <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">Unavailable</span>
          </div>
        )}
      </div>

      <div className="book-info">
        <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2">{book.title}</h4>

        <p className="text-gray-600 text-sm mb-2">by {book.author}</p>

        {book.ai_summary && <p className="text-gray-700 text-sm mb-3 line-clamp-3">{book.ai_summary}</p>}

        <div className="flex items-center gap-2 mb-3 text-xs text-gray-500">
          {book.genre && <span className="genre-tag">{book.genre}</span>}
          {book.publication_year && <span>{book.publication_year}</span>}
        </div>

        <div className="flex items-center justify-between mb-4">
          <span className={`availability-badge ${book.available_copies > 0 ? "available" : "unavailable"}`}>
            {book.available_copies > 0 ? `${book.available_copies}/${book.total_copies} available` : "Not available"}
          </span>

          {book.average_rating && (
            <div className="flex items-center gap-1">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="text-sm text-gray-600">{book.average_rating.toFixed(1)}</span>
            </div>
          )}
        </div>

        {showActions && (
          <div className="flex gap-2">
            <button
              className={`btn flex-1 ${book.available_copies > 0 ? "btn-primary" : "btn-secondary"}`}
              onClick={() => handleAction(book.available_copies > 0 ? onBorrow : onReserve, book.id)}
              disabled={actionLoading}
            >
              {actionLoading ? "Processing..." : book.available_copies > 0 ? "Borrow" : "Reserve"}
            </button>

            {onViewDetails && (
              <button className="btn btn-outline" onClick={() => onViewDetails(book)}>
                <ExternalLink className="w-4 h-4" />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )

  if (loading) {
    return (
      <div className="book-card loading">
        <div className="animate-pulse">
          <div className="bg-gray-200 rounded-lg h-64 mb-4"></div>
          <div className="bg-gray-200 rounded h-4 mb-2"></div>
          <div className="bg-gray-200 rounded h-4 w-3/4 mb-2"></div>
          <div className="bg-gray-200 rounded h-8 w-full"></div>
        </div>
      </div>
    )
  }

  switch (variant) {
    case "borrowed":
      return renderBorrowedVariant()
    case "search":
      return renderSearchVariant()
    default:
      return renderDefaultVariant()
  }
}

export default BookCard
