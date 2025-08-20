"use client"

import { useState } from "react"
import { Search, Filter, Book } from "lucide-react"
// import "../styles/components/BookSearch.css"

const BookSearch = ({ apiCall }) => {
  const [searchQuery, setSearchQuery] = useState("")
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    genre: "",
    author: "",
    availability: "all",
  })

  const handleSearch = async (query = searchQuery) => {
    if (!query.trim()) return

    setLoading(true)
    try {
      const response = await apiCall("/api/books/search", {
        method: "POST",
        body: JSON.stringify({ query, limit: 20 }),
      })
      setSearchResults(response.books)
    } catch (error) {
      console.error("Search error:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleReserveBook = async (bookId) => {
    try {
      const response = await apiCall("/reserve", {
        method: "POST",
        body: JSON.stringify({ book_id: bookId }),
      })
      alert(response.message)
      handleSearch()
    } catch (error) {
      alert("Error: " + error.message)
    }
  }

  const filteredResults = searchResults.filter((book) => {
    if (filters.genre && !book.genre?.toLowerCase().includes(filters.genre.toLowerCase())) {
      return false
    }
    if (filters.author && !book.author.toLowerCase().includes(filters.author.toLowerCase())) {
      return false
    }
    if (filters.availability === "available" && book.available_copies === 0) {
      return false
    }
    return true
  })

  return (
    <div className="book-search">
      <h1>📚 Search Books</h1>

      {/* Search Bar */}
      <div className="search-section">
        <div className="search-bar">
          <Search className="search-icon" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            placeholder="Search for books, authors, topics..."
            className="search-input"
          />
          <button onClick={() => handleSearch()} className="btn btn-primary" disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {/* Filters */}
        <div className="filters">
            <Filter className="filter-icon" />
              <select
             value={filters.genre}
            onChange={(e) => setFilters((prev) => ({ ...prev, genre: e.target.value }))}
            className="filter-select"
          >
            <option value="">All Genres</option>
            <option value="fiction">Fiction</option>
            <option value="science">Science</option>
              <option value="technology">Technology</option>
            <option value="history">History</option>
            <option value="biography">Biography</option>
          </select>

                    <input
                      type="text"
                      value={filters.author}
                      onChange={(e) => setFilters((prev) => ({ ...prev, author: e.target.value }))}
                      placeholder="Filter by author"
                      className="filter-input"
                    />

          <select
            value={filters.availability}
            onChange={(e) => setFilters((prev) => ({ ...prev, availability: e.target.value }))}
            className="filter-select"
          >
            <option value="all">All Books</option>
            <option value="available">Available Only</option>
          </select>
        </div>
      </div>

      {/* Quick Srch */}
      <div className="quick-searches">
        <h3>Popular Searches:</h3>
        <div className="suggestion-chips">
          {[
            "Machine Learning",
            "Data Structures",
            "Web Development",
            "Algorithms",
            "Database Systems",
            "Software Engineering",
          ].map((suggestion) => (
            <button
              key={suggestion}
              className="suggestion-chip"
              onClick={() => {
                setSearchQuery(suggestion)
                handleSearch(suggestion)
              }}
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* Search res */}
      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Searching library catalog...</p>
        </div>
      )}

      {filteredResults.length > 0 && (
        <div className="search-results">
          <h3>Search Results ({filteredResults.length} books found)</h3>
          <div className="results-grid">
            {filteredResults.map((book) => (
              <div key={book.id} className="book-result-card">
                <img src={book.image_url || "/placeholder-book.png"} alt={book.title} className="book-cover" />
                <div className="book-details">
                  <h4>{book.title}</h4>
                  <p className="author">by {book.author}</p>

                  {book.ai_summary && <p className="ai-summary">{book.ai_summary}</p>}

                  <div className="book-meta">
                    {book.genre && <span className="genre-tag">{book.genre}</span>}
                    {book.publication_year && <span className="year">{book.publication_year}</span>}
                  </div>

                  <div className="availability">
                    <span className={`availability-badge ${book.available_copies > 0 ? "available" : "unavailable"}`}>
                      {book.available_copies > 0 ? `${book.available_copies} available` : "Not available"}
                    </span>
                  </div>

                  <button
                    className={`btn ${book.available_copies > 0 ? "btn-primary" : "btn-secondary"}`}
                    onClick={() => handleReserveBook(book.id)}
                  >
                    {book.available_copies > 0 ? "📖 Issue Now" : "⏳ Join Waitlist"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {searchQuery && filteredResults.length === 0 && !loading && (
        <div className="no-results">
          <Book size={48} />
          <h3>No books found</h3>
          <p>Try adjusting your search terms or filters</p>
        </div>
      )}
    </div>
  )
}

export default BookSearch
