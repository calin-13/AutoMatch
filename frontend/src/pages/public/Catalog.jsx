import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { carsApi } from '../../api/cars'

const BODY_TYPES = [
  { value: 'sedan', label: 'Sedan' },
  { value: 'hatchback', label: 'Hatchback' },
  { value: 'suv', label: 'SUV' },
  { value: 'break', label: 'Break' },
  { value: 'coupe', label: 'Coupé' },
  { value: 'cabrio', label: 'Cabrio' },
  { value: 'minivan', label: 'Minivan' },
]

const FUEL_TYPES = [
  { value: 'benzina', label: 'Benzină' },
  { value: 'motorina', label: 'Motorină' },
  { value: 'hibrid', label: 'Hibrid' },
  { value: 'electric', label: 'Electric' },
]

const PAGE_SIZE = 12

function formatPrice(price) {
  if (price == null) return '—'
  return new Intl.NumberFormat('ro-RO').format(price) + ' €'
}

export default function Catalog() {
  const [cars, setCars] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [filters, setFilters] = useState({
    marca: '',
    tip_caroserie: '',
    tip_combustibil: '',
    pret_max: '',
    an_min: '',
  })

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const params = { page, page_size: PAGE_SIZE }
        Object.entries(filters).forEach(([k, v]) => {
          if (v !== '' && v != null) params[k] = v
        })
        const data = await carsApi.search(params)
        if (cancelled) return
        const list = data.cars || data.items || data.results || (Array.isArray(data) ? data : [])
        setCars(list)
        setTotal(data.total ?? data.count ?? list.length)
      } catch (err) {
        if (!cancelled) setError('Nu s-au putut încărca mașinile.')
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [page, filters])

  function setFilter(key, value) {
    setPage(1)
    setFilters(f => ({ ...f, [key]: value }))
  }

  function toggleFilter(key, value) {
    setPage(1)
    setFilters(f => ({ ...f, [key]: f[key] === value ? '' : value }))
  }

  function resetFilters() {
    setPage(1)
    setFilters({ marca: '', tip_caroserie: '', tip_combustibil: '', pret_max: '', an_min: '' })
  }

  const hasFilters = Object.values(filters).some(v => v !== '' && v != null)
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="mb-10">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-4">
          Catalog
        </div>
        <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
          Explorează <span className="italic text-accent">catalogul</span>.
        </h1>
        <p className="text-ink-muted text-lg max-w-xl">
          Toate mașinile disponibile. Filtrează după marcă, caroserie, combustibil sau preț.
        </p>
      </div>

      {/* Filters */}
      <div className="border border-line bg-surface p-6 mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-xs text-ink-muted uppercase tracking-wider mb-2">Marca</label>
            <input
              type="text"
              placeholder="ex: BMW"
              value={filters.marca}
              onChange={(e) => setFilter('marca', e.target.value)}
              className="w-full px-3 py-2 border border-line bg-canvas text-sm text-ink focus:outline-none focus:border-ink transition"
            />
          </div>
          <div>
            <label className="block text-xs text-ink-muted uppercase tracking-wider mb-2">Preț maxim (€)</label>
            <input
              type="number"
              placeholder="ex: 30000"
              value={filters.pret_max}
              onChange={(e) => setFilter('pret_max', e.target.value)}
              className="w-full px-3 py-2 border border-line bg-canvas text-sm text-ink focus:outline-none focus:border-ink transition"
            />
          </div>
          <div>
            <label className="block text-xs text-ink-muted uppercase tracking-wider mb-2">An minim</label>
            <input
              type="number"
              placeholder="ex: 2018"
              value={filters.an_min}
              onChange={(e) => setFilter('an_min', e.target.value)}
              className="w-full px-3 py-2 border border-line bg-canvas text-sm text-ink focus:outline-none focus:border-ink transition"
            />
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-xs text-ink-muted uppercase tracking-wider mb-2">Caroserie</label>
          <div className="flex flex-wrap gap-2">
            {BODY_TYPES.map(t => (
              <button
                key={t.value}
                type="button"
                onClick={() => toggleFilter('tip_caroserie', t.value)}
                className={`px-3 py-1.5 text-xs border transition ${
                  filters.tip_caroserie === t.value
                    ? 'border-ink bg-ink text-canvas'
                    : 'border-line text-ink-muted hover:border-ink/40 hover:text-ink'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-xs text-ink-muted uppercase tracking-wider mb-2">Combustibil</label>
          <div className="flex flex-wrap gap-2">
            {FUEL_TYPES.map(t => (
              <button
                key={t.value}
                type="button"
                onClick={() => toggleFilter('tip_combustibil', t.value)}
                className={`px-3 py-1.5 text-xs border transition ${
                  filters.tip_combustibil === t.value
                    ? 'border-ink bg-ink text-canvas'
                    : 'border-line text-ink-muted hover:border-ink/40 hover:text-ink'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {hasFilters && (
          <button
            onClick={resetFilters}
            className="text-xs text-ink-muted hover:text-ink transition mt-2"
          >
            ← Resetează filtrele
          </button>
        )}
      </div>

      <div className="text-sm text-ink-muted mb-6">
        {loading ? 'se caută...' : `${total} ${total === 1 ? 'mașină găsită' : 'mașini găsite'}`}
      </div>

      {error && (
        <div className="border border-danger/30 bg-danger/5 text-danger px-4 py-3 mb-6">
          {error}
        </div>
      )}

      {!loading && cars.length === 0 && !error && (
        <div className="text-center py-20 text-ink-muted">
          Nicio mașină nu se potrivește filtrelor selectate.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cars.map(car => (
          <Link
            to={`/cars/${car.id}`}
            key={car.id}
            className="border border-line bg-surface p-6 hover:border-ink/40 transition group"
          >
            <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-3">
              {car.tip_caroserie || '—'} · {car.tip_combustibil || '—'}
            </div>
            <h3 className="font-display text-2xl tracking-tight text-ink mb-1 group-hover:text-accent transition leading-tight">
              {car.marca} {car.model}
            </h3>
            <p className="text-sm text-ink-muted mb-4">{car.an}</p>
            <div className="flex items-baseline justify-between pt-4 border-t border-line">
              <span className="text-xl font-mono text-ink">{formatPrice(car.pret)}</span>
              <span className="text-xs text-ink-subtle font-mono">
                {car.putere_cp ? `${car.putere_cp} CP` : ''}
              </span>
            </div>
          </Link>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-12 pt-6 border-t border-line">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => Math.max(1, p - 1))}
            className="text-sm text-ink-muted hover:text-ink disabled:opacity-30 disabled:hover:text-ink-muted transition"
          >
            ← Anterior
          </button>
          <span className="text-sm font-mono text-ink-muted">
            Pagina {page} din {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            className="text-sm text-ink-muted hover:text-ink disabled:opacity-30 disabled:hover:text-ink-muted transition"
          >
            Următor →
          </button>
        </div>
      )}
    </div>
  )
}
