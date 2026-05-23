import { NavLink } from 'react-router-dom'

export default function AdminNav() {
  const linkClass = ({ isActive }) =>
    `text-sm transition pb-3 -mb-px border-b-2 ${
      isActive
        ? 'border-accent text-accent'
        : 'border-transparent text-ink-muted hover:text-ink'
    }`
  return (
    <div className="border-b border-line mb-12">
      <nav className="max-w-6xl mx-auto px-6 flex gap-8">
        <NavLink to="/admin" end className={linkClass}>Dashboard</NavLink>
        <NavLink to="/admin/users" className={linkClass}>Utilizatori</NavLink>
      </nav>
    </div>
  )
}
