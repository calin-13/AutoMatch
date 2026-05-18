import { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '../api/auth'
import { TOKEN_KEY, setUnauthorizedHandler } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [loading, setLoading] = useState(true)

  // Sincronizează AuthContext cu interceptor-ul axios pe 401
  useEffect(() => {
    setUnauthorizedHandler(() => {
      setToken(null)
      setUser(null)
    })
    return () => setUnauthorizedHandler(null)
  }, [])

  useEffect(() => {
    async function bootstrap() {
      if (!token) {
        setLoading(false)
        return
      }
      try {
        const me = await authApi.me()
        setUser(me)
      } catch {
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
      } finally {
        setLoading(false)
      }
    }
    bootstrap()
  }, [])

  async function login(email, password) {
    const { access_token } = await authApi.login(email, password)
    localStorage.setItem(TOKEN_KEY, access_token)
    setToken(access_token)
    const me = await authApi.me()
    setUser(me)
    return me
  }

  async function register(email, username, password) {
    const { access_token } = await authApi.register(email, username, password)
    localStorage.setItem(TOKEN_KEY, access_token)
    setToken(access_token)
    const me = await authApi.me()
    setUser(me)
    return me
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
