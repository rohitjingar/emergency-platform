import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const storedUser = localStorage.getItem('user')
    const token = localStorage.getItem('access_token')
    if (storedUser && token) {
      setUser(JSON.parse(storedUser))
      setIsAuthenticated(true)
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password })
    const { access_token, role } = response.data
    
    localStorage.setItem('access_token', access_token)
    
    const userData = { email, role }
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
    setIsAuthenticated(true)
    
    return response.data
  }

  const register = async (email, password, role) => {
    const response = await authAPI.register({ email, password, role })
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
    setIsAuthenticated(false)
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
