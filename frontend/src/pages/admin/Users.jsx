import { useState, useEffect } from 'react'
import AdminNav from '../../components/layout/AdminNav'
import { useAuth } from '../../context/AuthContext'
import { adminApi } from '../../api/admin'

function formatDate(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleDateString('ro-RO', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

function UserRow({ user, currentUserId, onPromote, onDemote, onDelete, busy }) {
  const isAdmin = user.role === 'admin'
  const isSelf = user.id === currentUserId
  const recsCount = user.recommendations_count ?? user.recs_count ?? user.total_recommendations ?? 0
  const fbCount = user.feedback_count ?? user.feedbacks_count ?? user.total_feedback ?? 0
  const hasProfile = user.has_profile ?? user.profile_complete ?? false

  return (
    <div className="border border-line bg-surface p-5 flex items-center justify-between gap-6 flex-wrap">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-3 mb-1 flex-wrap">
          <span className="text-base text-ink font-medium">{user.username}</span>
          {isAdmin && (
            <span className="text-xs font-mono uppercase tracking-widest text-accent border border-accent/30 px-2 py-0.5">
              Admin
            </span>
          )}
          {isSelf && (
            <span className="text-xs font-mono uppercase tracking-widest text-ink-muted">
              (tu)
            </span>
          )}
        </div>
        <div className="text-sm text-ink-muted truncate">{user.email}</div>
        <div className="text-xs text-ink-subtle mt-2 font-mono">
          {recsCount} {recsCount === 1 ? 'recomandare' : 'recomandări'} ·{' '}
          {fbCount} feedback ·{' '}
          {hasProfile ? 'profil complet' : 'profil incomplet'} ·{' '}
          înregistrat {formatDate(user.created_at)}
        </div>
      </div>

      <div className="flex items-center gap-2 flex-shrink-0">
        {!isSelf && (
          <>
            {isAdmin ? (
              <button
                onClick={() => onDemote(user.id)}
                disabled={busy}
                className="px-3 py-2 text-xs border border-line text-ink-muted hover:border-ink/40 hover:text-ink transition disabled:opacity-50"
              >
                Retrogradează
              </button>
            ) : (
              <button
                onClick={() => onPromote(user.id)}
                disabled={busy}
                className="px-3 py-2 text-xs border border-accent/40 text-accent hover:border-accent transition disabled:opacity-50"
              >
                Promovează
              </button>
            )}
            <button
              onClick={() => onDelete(user.id, user.username)}
              disabled={busy}
              className="px-3 py-2 text-xs border border-line text-ink-muted hover:border-danger hover:text-danger transition disabled:opacity-50"
            >
              Șterge
            </button>
          </>
        )}
      </div>
    </div>
  )
}

export default function Users() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionBusy, setActionBusy] = useState({})
  const [query, setQuery] = useState('')

  useEffect(() => {
    load()
  }, [])

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const data = await adminApi.getUsers()
      const list = data.users || data.items || (Array.isArray(data) ? data : [])
      setUsers(list)
    } catch (err) {
      setError('Nu s-au putut încărca utilizatorii.')
    } finally {
      setLoading(false)
    }
  }

  async function runAction(userId, fn, errMsg) {
    setActionBusy((s) => ({ ...s, [userId]: true }))
    try {
      await fn(userId)
      await load()
    } catch (err) {
      alert(errMsg)
    } finally {
      setActionBusy((s) => ({ ...s, [userId]: false }))
    }
  }

  async function handleDelete(userId, username) {
    const ok = window.confirm(
      `Sigur vrei să ștergi utilizatorul "${username}"?\n\nAceastă acțiune este permanentă și va șterge profilul, recomandările și feedback-ul asociat.`
    )
    if (!ok) return
    await runAction(userId, adminApi.deleteUser, 'Nu s-a putut șterge utilizatorul.')
  }

  const filtered = query
    ? users.filter(u =>
        (u.username || '').toLowerCase().includes(query.toLowerCase()) ||
        (u.email || '').toLowerCase().includes(query.toLowerCase())
      )
    : users

  const admins = filtered.filter(u => u.role === 'admin').length
  const regular = filtered.length - admins

  return (
    <>
      <AdminNav />
      <div className="max-w-6xl mx-auto px-6 pb-12">
        <div className="mb-10">
          <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
            Admin · Utilizatori
          </div>
          <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
            <span className="italic text-accent">{users.length}</span> utilizatori înregistrați.
          </h1>
          <p className="text-ink-muted text-lg">
            {regular} {regular === 1 ? 'utilizator' : 'utilizatori'} · {admins} {admins === 1 ? 'admin' : 'admini'}
          </p>
        </div>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Caută după username sau email..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full max-w-md px-4 py-2 border border-line bg-surface text-sm text-ink focus:outline-none focus:border-ink transition"
          />
        </div>

        {loading && (
          <div className="text-center py-20">
            <span className="text-sm text-ink-muted font-mono uppercase tracking-widest">se încarcă...</span>
          </div>
        )}

        {error && (
          <div className="border border-danger/30 bg-danger/5 text-danger px-4 py-3 mb-6">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="space-y-3">
            {filtered.length === 0 ? (
              <div className="text-center py-20 text-ink-muted">
                {query ? 'Niciun utilizator nu se potrivește căutării.' : 'Niciun utilizator înregistrat.'}
              </div>
            ) : (
              filtered.map((u) => (
                <UserRow
                  key={u.id}
                  user={u}
                  currentUserId={currentUser?.id}
                  busy={!!actionBusy[u.id]}
                  onPromote={(id) => runAction(id, adminApi.promoteUser, 'Nu s-a putut promova utilizatorul.')}
                  onDemote={(id) => runAction(id, adminApi.demoteUser, 'Nu s-a putut retrograda utilizatorul.')}
                  onDelete={handleDelete}
                />
              ))
            )}
          </div>
        )}
      </div>
    </>
  )
}
