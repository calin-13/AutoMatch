import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { carsApi } from '../../api/cars'
import { feedbackApi } from '../../api/feedback'
import CarImagePlaceholder from '../../components/CarImagePlaceholder'

const FIELD_CONFIG = {
  putere_cp: { label: 'Putere', unit: 'CP' },
  consum_mediu: { label: 'Consum mediu', unit: 'l/100km' },
  emisii_co2: { label: 'Emisii CO₂', unit: 'g/km' },
  lungime_mm: { label: 'Lungime', unit: 'mm' },
  latime_mm: { label: 'Lățime', unit: 'mm' },
  inaltime_mm: { label: 'Înălțime', unit: 'mm' },
  numar_locuri: { label: 'Locuri' },
  volum_portbagaj: { label: 'Portbagaj', unit: 'l' },
}

const SECTIONS = [
  { title: 'Motor & Consum', fields: ['putere_cp', 'consum_mediu', 'emisii_co2'] },
  { title: 'Spațiu interior', fields: ['numar_locuri', 'volum_portbagaj'] },
  { title: 'Dimensiuni exterioare', fields: ['lungime_mm', 'latime_mm', 'inaltime_mm'] },
]

const RATING_AXES = [
  { key: 'rating_siguranta', label: 'Siguranță' },
  { key: 'rating_comfort', label: 'Confort' },
  { key: 'rating_sport', label: 'Sport' },
  { key: 'rating_economie', label: 'Economie' },
  { key: 'rating_estetica', label: 'Estetică' },
]

function formatValue(value, unit) {
  if (value == null || value === '') return '—'
  const formatted = typeof value === 'number'
    ? new Intl.NumberFormat('ro-RO').format(value)
    : String(value)
  return unit ? `${formatted} ${unit}` : formatted
}

function formatPrice(price) {
  if (price == null) return '—'
  return new Intl.NumberFormat('ro-RO').format(price) + ' €'
}

export default function CarDetails() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const [car, setCar] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [userRating, setUserRating] = useState(0)
  const [feedbackSubmitting, setFeedbackSubmitting] = useState(false)
  const [feedbackSaved, setFeedbackSaved] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        const data = await carsApi.getById(id)
        if (!cancelled) setCar(data)
      } catch (err) {
        if (!cancelled) {
          setError(err.response?.status === 404 ? 'notfound' : 'generic')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [id])

  async function submitFeedback(rating) {
    if (!isAuthenticated) {
      navigate('/login', { state: { from: { pathname: `/cars/${id}` } } })
      return
    }
    if (feedbackSubmitting || !car) return
    setFeedbackSubmitting(true)
    setFeedbackSaved(false)
    const newRating = userRating === rating ? 0 : rating
    try {
      await feedbackApi.submit(car.id, newRating)
      setUserRating(newRating)
      setFeedbackSaved(true)
      setTimeout(() => setFeedbackSaved(false), 2000)
    } catch {
      // silent
    } finally {
      setFeedbackSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-32 text-center">
        <div className="text-sm text-ink-muted font-mono uppercase tracking-widest">
          se încarcă...
        </div>
      </div>
    )
  }

  if (error === 'notfound' || !car) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-32 text-center">
        <h1 className="font-display text-5xl tracking-tight text-ink mb-4">
          Mașina nu a fost găsită.
        </h1>
        <p className="text-ink-muted mb-8">Poate a fost scoasă din catalog sau ID-ul este greșit.</p>
        <Link to="/recommendations" className="text-accent hover:underline">
          ← Înapoi la recomandări
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <button
        onClick={() => navigate(-1)}
        className="text-sm text-ink-muted hover:text-ink transition mb-8"
      >
        ← Înapoi
      </button>

      <CarImagePlaceholder
        marca={car.marca}
        model={car.model}
        an={car.an}
        tipCaroserie={car.tip_caroserie}
        tipCombustibil={car.tip_combustibil}
      />
      {/* Hero */}
      <div className="border-b border-line pb-12 mb-12">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-4">
          {car.tip_caroserie || '—'} · {car.tip_combustibil || '—'}
        </div>
        <h1 className="font-display text-6xl tracking-tightest text-ink leading-[0.95] mb-4">
          {car.marca} <span className="italic">{car.model}</span>
        </h1>
        <p className="text-xl text-ink-muted mb-8">{car.an}</p>
        <div className="text-4xl font-mono text-ink">
          {formatPrice(car.pret)}
        </div>
      </div>

      {/* Specs sections */}
      <div className="space-y-12 mb-16">
        {SECTIONS.map((section) => {
          const items = section.fields
            .map((key) => {
              const value = car[key]
              if (value == null || value === '') return null
              const config = FIELD_CONFIG[key] || { label: key }
              return { key, label: config.label, value, unit: config.unit }
            })
            .filter(Boolean)

          if (items.length === 0) return null

          return (
            <section key={section.title}>
              <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
                {section.title}
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-6">
                {items.map((item) => (
                  <div key={item.key}>
                    <div className="text-xs text-ink-subtle uppercase tracking-wider mb-1">
                      {item.label}
                    </div>
                    <div className="text-lg text-ink font-mono">
                      {formatValue(item.value, item.unit)}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )
        })}
      </div>

      {/* Profilul mașinii */}
      <div className="border-t border-line pt-12 mb-12">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-2">
          Profilul mașinii
        </div>
        <h2 className="font-display text-3xl tracking-tight text-ink mb-2">
          Cum se <span className="italic text-accent">comportă</span>.
        </h2>
        <p className="text-sm text-ink-muted mb-8 max-w-xl">
          Cele cinci axe pe care e evaluată fiecare mașină din catalog —
          aceleași cu profilul tău din mini-test.
        </p>

        <div className="space-y-5">
          {RATING_AXES.map((axis) => {
            const rating = car[axis.key] ?? 0
            const pct = (rating / 5) * 100
            return (
              <div key={axis.key}>
                <div className="flex items-baseline justify-between mb-2">
                  <span className="text-sm text-ink">{axis.label}</span>
                  <span className="text-sm font-mono text-ink-muted">
                    {rating.toFixed(1)}<span className="text-ink-subtle">/5</span>
                  </span>
                </div>
                <div className="h-1.5 bg-line overflow-hidden">
                  <div
                    className="h-full bg-ink transition-all duration-700"
                    style={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Feedback */}
      <div className="mt-12 pt-8 border-t border-line">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-4">
          Ce părere ai?
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => submitFeedback(1)}
            disabled={feedbackSubmitting}
            className={`px-5 py-3 text-sm border transition ${
              userRating === 1
                ? 'border-accent bg-accent/5 text-accent'
                : 'border-line text-ink-muted hover:border-ink/40 hover:text-ink'
            } disabled:opacity-50`}
          >
            Îmi place
          </button>
          <button
            onClick={() => submitFeedback(-1)}
            disabled={feedbackSubmitting}
            className={`px-5 py-3 text-sm border transition ${
              userRating === -1
                ? 'border-ink bg-ink/[0.05] text-ink'
                : 'border-line text-ink-muted hover:border-ink/40 hover:text-ink'
            } disabled:opacity-50`}
          >
            Nu-mi place
          </button>
          {feedbackSaved && (
            <span className="text-xs text-ink-muted ml-2">
              feedback salvat
            </span>
          )}
        </div>
        {!isAuthenticated && (
          <p className="text-xs text-ink-muted mt-3">
            <Link to="/login" className="hover:text-ink transition underline">Conectează-te</Link>
            {' '}ca să-ți salvăm preferințele.
          </p>
        )}
      </div>
    </div>
  )
}
