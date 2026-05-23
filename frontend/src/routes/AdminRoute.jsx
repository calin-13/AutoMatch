import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function AdminRoute({ children }) {
  const { isAuthenticated, isAdmin, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="text-sm text-ink-muted font-mono uppercase tracking-widest">
          se încarcă...
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!isAdmin) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-32 text-center">
        <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
          Acces restricționat.
        </h1>
        <p className="text-ink-muted">
          Această secțiune e disponibilă doar pentru administratori.
        </p>
      </div>
    )
  }

  return children
}
