import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'

const AuthContext = createContext()

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.get('/api/auth/me')
        .then(r => setUser(r.data))
        .catch(() => localStorage.removeItem('token'))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const register = async (data) => {
    const r = await api.post('/api/auth/register', data)
    // If auto-approved (CEO), log them in
    if (r.data.status === 'approved') {
      return login(data.email, data.password)
    }
    return r.data
  }

  const login = async (email, password) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', password)
    const r = await api.post('/api/auth/login', formData)
    localStorage.setItem('token', r.data.access_token)
    const me = await api.get('/api/auth/me')
    setUser(me.data)
    return me.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, loading, register, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
