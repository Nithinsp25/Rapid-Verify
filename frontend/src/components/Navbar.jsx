import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false)
  const location = useLocation()

  return (
    <nav className="navbar glass-panel">
      <div className="nav-container">
        <Link to="/" className="logo">
          <div className="logo-icon pulse-glow">
            <i className="fas fa-shield-halved"></i>
          </div>
          <span className="logo-text">Rapid<span className="accent">Verify</span></span>
        </Link>
        
        <ul className={`nav-links ${menuOpen ? 'active' : ''}`}>
          <li><Link to="/" className={location.pathname === '/' ? 'active' : ''}>Home</Link></li>
          <li><Link to="/verify" className={location.pathname === '/verify' ? 'active' : ''}>Verify</Link></li>
          <li><Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>Dashboard</Link></li>
        </ul>
        
        <div 
          className={`mobile-menu-btn ${menuOpen ? 'active' : ''}`}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </nav>
  )
}
