import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  const linkClass = ({ isActive }) =>
    `transition ${isActive ? 'text-ink' : 'text-ink-muted hover:text-ink'}`

  return (
    <header className="border-b border-line bg-canvas/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between gap-4">
        <Link to="/" className="font-display text-2xl tracking-tight text-ink flex-shrink-0">
          Auto<span className="italic text-accent">Match</span>
        </Link>

        <nav className="hidden sm:flex items-center gap-6 text-sm">
          <NavLink to="/" end className={linkClass}>Acasă</NavLink>
          {isAuthenticated && (
            <NavLink to="/recommendations" className={linkClass}>Recomandări</NavLink>
          )}
          <NavLink to="/catalog" className={linkClass}>Catalog</NavLink>
        </nav>

        <div className="flex items-center gap-4 flex-shrink-0">
          {isAuthenticated ? (
            <>
              <Link
                to="/profile"
                className="text-sm text-ink hover:text-accent transition"
                title="Vezi profilul"
              >
                {user?.username}
              </Link>
              <button
                onClick={handleLogout}
                className="text-sm text-ink-muted hover:text-ink transition"
              >
                Deconectare
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm text-ink-muted hover:text-ink transition">
                Conectează-te
              </Link>
              <Link to="/register" className="text-sm px-4 py-2 bg-ink text-canvas hover:bg-ink/90 transition">
                Cont nou
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
