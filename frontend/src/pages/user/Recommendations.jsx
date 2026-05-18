import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { recommendationsApi } from '../../api/recommendations'
import { feedbackApi } from '../../api/feedback'

const AXES = [
  { key: 'comfort', label: 'Confort' },
  { key: 'sport', label: 'Sport' },
  { key: 'siguranta', label: 'Siguranță' },
  { key: 'economie', label: 'Economie' },
  { key: 'estetica', label: 'Estetică' },
]

function formatPrice(price) {
  if (price == null) return '—'
  return new Intl.NumberFormat('ro-RO').format(price) + ' €'
}

function humanizeFeature(name, impact) {
  if (!name) return ''
  const positive = impact > 0
  const key = name.toLowerCase()
  const map = {
    pret: positive ? 'În bugetul tău' : 'Peste bugetul tău',
    consum: positive ? 'Consum eficient' : 'Consum ridicat',
    consum_combustibil: positive ? 'Consum eficient' : 'Consum ridicat',
    consum_mixt: positive ? 'Consum mixt eficient' : 'Consum mixt ridicat',
    consum_oras: positive ? 'Eficient în oraș' : 'Consum mare în oraș',
    consum_extraurban: positive ? 'Eficient pe șosea' : 'Consum mare pe șosea',
    an: positive ? 'Mașină recentă' : 'An de fabricație vechi',
    an_fabricatie: positive ? 'Mașină recentă' : 'An de fabricație vechi',
    putere: positive ? 'Putere potrivită profilului tău' : 'Putere ne-aliniată',
    putere_cp: positive ? 'Putere potrivită profilului tău' : 'Putere ne-aliniată',
    cilindree: positive ? 'Cilindree potrivită' : 'Cilindree ne-potrivită',
    siguranta: positive ? 'Siguranță foarte bună' : 'Siguranță sub medie',
    siguranta_euro_ncap: positive ? 'Scor Euro NCAP excelent' : 'Scor Euro NCAP mediu',
    volum_portbagaj: positive ? 'Portbagaj încăpător' : 'Portbagaj mic',
    numar_locuri: positive ? 'Număr de locuri potrivit' : 'Mai puține locuri decât ai vrea',
    numar_usi: positive ? 'Configurație potrivită' : 'Configurație ne-potrivită',
    lungime: positive ? 'Dimensiuni potrivite' : 'Dimensiuni ne-potrivite',
    spatiu_picioare: positive ? 'Spațiu generos pentru picioare' : 'Spațiu limitat pentru picioare',
    inaltime_garda: positive ? 'Gardă la sol potrivită' : 'Gardă la sol ne-aliniată',
    tip_combustibil: positive ? 'Tip combustibil preferat' : 'Combustibil diferit de preferința ta',
    tip_caroserie: positive ? 'Caroserie pe gustul tău' : 'Caroserie ne-aliniată cu profilul',
    cutie_viteze: positive ? 'Cutie de viteze potrivită' : 'Cutie ne-potrivită',
    tractiune: positive ? 'Tracțiune potrivită' : 'Tracțiune ne-potrivită',
    comfort: positive ? 'Confort pe măsura ta' : 'Confort sub așteptările tale',
    sport: positive ? 'Caracter sportiv potrivit' : 'Mai puțin sportivă',
    economie: positive ? 'Economică pentru utilizarea ta' : 'Mai puțin economică',
    estetica: positive ? 'Design pe gustul tău' : 'Design ne-aliniat profilului',
    masa: positive ? 'Masă echilibrată' : 'Masă ne-potrivită',
    viteza_maxima: positive ? 'Viteză maximă potrivită' : 'Viteză maximă ne-potrivită',
  }
  if (map[key]) return map[key]
  const pretty = name.replace(/_/g, ' ')
  return positive ? `${pretty} aliniat profilului` : `${pretty} ne-aliniat`
}

function Spec({ label, value }) {
  return (
    <div>
      <div className="text-xs text-ink-subtle uppercase tracking-wider mb-1">{label}</div>
      <div className="text-sm text-ink">{value || '—'}</div>
    </div>
  )
}

function FeedbackButton({ active, onClick, disabled, variant, children }) {
  const activeStyle =
    variant === 'positive'
      ? 'border-accent bg-accent/5 text-accent'
      : 'border-ink bg-ink/[0.05] text-ink'
  const inactiveStyle = 'border-line text-ink-muted hover:border-ink/40 hover:text-ink'
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-4 py-2 text-sm border transition ${active ? activeStyle : inactiveStyle} disabled:opacity-50`}
    >
      {children}
    </button>
  )
}

export default function Recommendations() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [diversity, setDiversity] = useState(false)
  const [feedbacks, setFeedbacks] = useState({})
  const [feedbackSubmitting, setFeedbackSubmitting] = useState({})

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const result = await recommendationsApi.getFromProfile(diversity)
        if (!cancelled) setData(result)
      } catch (err) {
        if (cancelled) return
        if (err.response?.status === 400) {
          setError({ type: 'incomplete', detail: err.response.data?.detail })
        } else {
          setError({ type: 'generic' })
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [diversity])

  async function submitFeedback(carId, rating) {
    if (feedbackSubmitting[carId]) return
    setFeedbackSubmitting((s) => ({ ...s, [carId]: true }))
    const newRating = feedbacks[carId] === rating ? 0 : rating
    try {
      await feedbackApi.submit(carId, newRating, data?.recommendation_id)
      setFeedbacks((f) => ({ ...f, [carId]: newRating }))
    } catch {
      // ignorăm silent — utilizatorul poate reîncerca
    } finally {
      setFeedbackSubmitting((s) => ({ ...s, [carId]: false }))
    }
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-32 text-center">
        <div className="text-sm text-ink-muted font-mono uppercase tracking-widest animate-pulse">
          calculăm recomandările...
        </div>
      </div>
    )
  }

  if (error?.type === 'incomplete') {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20">
        <h1 className="font-display text-5xl tracking-tight text-ink mb-4">
          Profilul tău e incomplet.
        </h1>
        <p className="text-ink-muted mb-8">
          {typeof error.detail === 'string' ? error.detail : 'Completează datele ergonomice ca să primești recomandări.'}
        </p>
        <Link
          to="/profile"
          className="inline-block px-6 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition"
        >
          Completează profilul →
        </Link>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20">
        <div className="border border-danger/30 bg-danger/5 text-danger px-4 py-3">
          Nu s-au putut încărca recomandările. Încearcă din nou peste o secundă.
        </div>
      </div>
    )
  }

  const recommendations = data.recommendations || []
  const userProfile = data.user_profile || {}

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="mb-12">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
          Recomandările tale · Top 5
        </div>
        <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
          Pentru <span className="italic text-accent">{user?.username}</span>.
        </h1>
        <p className="text-ink-muted text-lg max-w-2xl">
          Cele 5 mașini care se potrivesc cel mai bine profilului tău. Pentru
          fiecare vezi motivele exacte și poți marca ce-ți place sau nu —
          recomandările viitoare se vor adapta.
        </p>
      </div>

      {/* Profile summary */}
      <div className="mb-10 p-6 border border-line bg-surface">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-5">
          Profilul tău din mini-test
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-5">
          {AXES.map((axis) => {
            const value = userProfile[axis.key] ?? 0
            return (
              <div key={axis.key}>
                <div className="flex items-baseline justify-between mb-2">
                  <span className="text-xs text-ink-muted uppercase tracking-wider">{axis.label}</span>
                  <span className="text-sm font-mono text-ink">{Math.round(value)}%</span>
                </div>
                <div className="h-1 bg-line overflow-hidden">
                  <div
                    className="h-full bg-ink transition-all duration-700"
                    style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Diversity toggle */}
      <div className="mb-8 flex items-center justify-between flex-wrap gap-3">
        <p className="text-sm text-ink-muted">
          {recommendations.length} {recommendations.length === 1 ? 'recomandare' : 'recomandări'}
        </p>
        <button
          type="button"
          onClick={() => setDiversity(!diversity)}
          className="flex items-center gap-3 text-sm group"
        >
          <span className={`transition ${diversity ? 'text-ink' : 'text-ink-muted group-hover:text-ink'}`}>
            Recomandări diverse
          </span>
          <span className={`relative w-10 h-5 transition ${diversity ? 'bg-accent' : 'bg-line'}`}>
            <span
              className={`absolute top-0.5 w-4 h-4 bg-canvas transition-transform ${
                diversity ? 'translate-x-[1.375rem]' : 'translate-x-0.5'
              }`}
            />
          </span>
        </button>
      </div>

      {/* Recommendations list */}
      <div className="space-y-6">
        {recommendations.map((rec, idx) => {
          const car = rec.car || rec
          const scoreDetails = rec.score_details || {}
          const explanation = scoreDetails.explanation || {}
          const topFeatures = explanation.top_features || []
          const carId = car.id
          const userRating = feedbacks[carId] ?? 0
          const positiveReasons = topFeatures.filter((f) => f.impact > 0).slice(0, 3)
          const negativeReasons = topFeatures.filter((f) => f.impact < 0).slice(0, 1)

          return (
            <article
              key={carId || idx}
              className="border border-line bg-surface p-8 hover:border-ink/20 transition"
            >
              <div className="flex flex-col lg:flex-row gap-8">
                {/* Left */}
                <div className="lg:w-1/3">
                  <div className="text-xs font-mono text-accent mb-3">
                    {String(idx + 1).padStart(2, '0')} · Recomandat
                  </div>
                  <h2 className="font-display text-3xl tracking-tight text-ink mb-1 leading-tight">
                    {car.marca} {car.model}
                  </h2>
                  <p className="text-sm text-ink-muted mb-5">{car.an}</p>
                  <div className="text-2xl font-mono text-ink">
                    {formatPrice(car.pret)}
                  </div>
                </div>

                {/* Right */}
                <div className="lg:w-2/3">
                  {/* Score */}
                  <div className="mb-6">
                    <div className="flex items-baseline justify-between mb-2">
                      <span className="text-xs text-ink-muted uppercase tracking-wider">
                        Potrivire cu profilul tău
                      </span>
                      <span className="text-sm font-mono text-ink">
                        {Math.round(rec.score_total ?? 0)}%
                      </span>
                    </div>
                    <div className="h-1 bg-line overflow-hidden">
                      <div
                        className="h-full bg-accent transition-all duration-700"
                        style={{ width: `${Math.min(100, Math.max(0, rec.score_total ?? 0))}%` }}
                      />
                    </div>
                  </div>

                  {/* Specs */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6 pb-6 border-b border-line">
                    <Spec label="Combustibil" value={car.tip_combustibil} />
                    <Spec label="Putere" value={car.putere ? `${car.putere} CP` : null} />
                    <Spec
                      label="Consum"
                      value={
                        car.consum_mixt
                          ? `${car.consum_mixt} l/100km`
                          : car.consum
                          ? `${car.consum} l/100km`
                          : null
                      }
                    />
                    <Spec label="Caroserie" value={car.tip_caroserie} />
                  </div>

                  {/* Motives */}
                  <div className="mb-6">
                    <div className="text-xs text-ink-muted uppercase tracking-wider mb-3">
                      De ce ți se potrivește
                    </div>
                    {positiveReasons.length > 0 ? (
                      <ul className="space-y-2">
                        {positiveReasons.map((f, i) => (
                          <li key={i} className="text-sm text-ink flex items-start gap-3">
                            <span className="text-accent mt-0.5 font-mono text-xs">+</span>
                            <span>{humanizeFeature(f.name, f.impact)}</span>
                          </li>
                        ))}
                        {negativeReasons.map((f, i) => (
                          <li key={`neg-${i}`} className="text-sm text-ink-muted flex items-start gap-3 mt-3 pt-3 border-t border-line">
                            <span className="text-ink-subtle mt-0.5 font-mono text-xs">−</span>
                            <span>{humanizeFeature(f.name, f.impact)}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-ink-muted italic">
                        Mașină echilibrată pentru profilul tău.
                      </p>
                    )}
                  </div>

                  {/* Feedback */}
                  <div className="flex items-center gap-2">
                    <FeedbackButton
                      active={userRating === 1}
                      onClick={() => submitFeedback(carId, 1)}
                      disabled={feedbackSubmitting[carId]}
                      variant="positive"
                    >
                      Îmi place
                    </FeedbackButton>
                    <FeedbackButton
                      active={userRating === -1}
                      onClick={() => submitFeedback(carId, -1)}
                      disabled={feedbackSubmitting[carId]}
                      variant="negative"
                    >
                      Nu-mi place
                    </FeedbackButton>
                    {userRating !== 0 && (
                      <span className="text-xs text-ink-muted ml-2">
                        feedback salvat
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </article>
          )
        })}
      </div>

      {recommendations.length === 0 && (
        <div className="text-center py-20 text-ink-muted">
          Momentan nu există recomandări disponibile pentru profilul tău.
        </div>
      )}
    </div>
  )
}
