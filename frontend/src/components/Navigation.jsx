"use client"
import { Link, useLocation } from "react-router-dom"
import { useAuth } from "../App"
import { Home, MessageCircle, Search, User, Book, LogOut } from "lucide-react"
import "../styles/Navigation.css"

const Navigation = () => {
  const location = useLocation()
  const { user, logout } = useAuth()

  const navItems = [
    { path: "/chat", icon: MessageCircle, label: "Chat Assistant" },
    { path: "/search", icon: Search, label: "Search Books" },
  ]

  return (
    <nav className="navigation">
      <div className="nav-brand">
        <Book className="brand-icon" />
        <span className="brand-text">LibriPal</span>
      </div>

      <div className="nav-items">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? "active" : ""}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </div>

      <div className="nav-user">
        <span className="welcome-text">Welcome, {user?.first_name || user?.username}!</span>
        <button onClick={logout} className="logout-btn" title="Logout">
          <LogOut size={20} />
        </button>
      </div>
    </nav>
  )
}

export default Navigation
