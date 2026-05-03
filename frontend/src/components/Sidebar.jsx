import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

export default function Sidebar() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()

  const isAdmin = user?.role === 'ceo' || user?.role === 'head'

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">⚡ TaskForge</div>
        <div className="text-xs text-muted" style={{ marginTop: 4 }}>Org-Based v2</div>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          📊 Dashboard
        </NavLink>
        <NavLink to="/organization" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          🏢 Directory
        </NavLink>
        {isAdmin && (
          <NavLink to="/approvals" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            🛂 Approvals
          </NavLink>
        )}
      </nav>

      <div className="sidebar-footer">
        <div className="user-profile mb-md">
          <div className="user-avatar">{user?.name?.[0]}</div>
          <div className="user-info">
            <div className="user-name">{user?.name}</div>
            <div className="user-role badge badge-sm" style={{ background: 'var(--bg-app)', border: '1px solid var(--border)' }}>{user?.role}</div>
          </div>
        </div>
        
        <div className="flex gap-sm">
          <button className="btn btn-ghost btn-sm full-width" onClick={toggleTheme}>
            {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
          </button>
          <button className="btn btn-ghost btn-sm full-width text-danger" onClick={logout}>
            🚪 Logout
          </button>
        </div>
      </div>
    </div>
  )
}
