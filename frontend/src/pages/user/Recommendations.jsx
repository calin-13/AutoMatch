import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { recommendationsApi } from '../../api/recommendations'
import { feedbackApi } from '../../api/feedback'
import { carsApi } from '../../api/cars'

const SHAP_SHORT_LABELS = {
  car_rating_siguranta: 'Siguranță (mașină)',
  car_rating_comfort: 'Confort (mașină)',
  car_rating_sport: 'Sport (mașină)',
  car_rating_economie: 'Economie (mașină)',
  car_rating_estetica: 'Estetică (mașină)',
  pref_siguranta: 'Pref. siguranță',
  pref_comfort: 'Pref. confort',
  pref_sport: 'Pref. sport',
  pref_economie: 'Pref. economie',
  pref_estetica: 'Pref. estetică',
  budget: 'Buget',
  user_budget: 'Buget',
  pret: 'Preț',
  price: 'Preț',
  putere_cp: 'Putere',
  consum_mediu: 'Consum',
  emisii_co2: 'Emisii CO₂',
  an: 'An fabricație',
  numar_locuri: 'Locuri',
  volum_portbagaj: 'Portbagaj',
  user_inaltime: 'Înălțime',
  inaltime: 'Înălțime',
  user_greutate: 'Greutate',
  greutate: 'Greutate',
  km_zi: 'Km/zi',
  user_km_zi: 'Km/zi',
  car_pret: 'Preț (mașină)',
  car_putere_cp: 'Putere',
  car_consum_mediu: 'Consum',
  car_emisii_co2: 'Emisii CO₂',
  car_volum_portbagaj: 'Portbagaj',
  car_numar_locuri: 'Locuri',
  car_is_electric: 'Electrică',
  car_is_hybrid: 'Hibridă',
  car_is_suv: 'SUV',
  car_is_coupe: 'Coupé',
  car_is_sedan: 'Sedan',
  price_ratio: 'Raport preț/buget',
}

function shapLabel(feature) {
  return SHAP_SHORT_LABELS[feature] || feature
}

function ShapChart({ features, baseValue }) {
  if (!features || features.length === 0) return null
  const maxAbs = Math.max(...features.map(f => Math.abs(Number(f.shap_value) || 0)), 0.1)

  return (
    <div className="mt-4 pt-4 border-t border-line">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-2">
        Analiză SHAP
      </div>
      <p className="text-xs text-ink-subtle mb-4 leading-relaxed">
        Contribuția fiecărui factor la scorul final. Pozitiv = ridică scorul,
        negativ = scade scorul. Calculat cu SHAP TreeExplainer pe Random Forest.
      </p>
      <div className="space-y-2.5">
        {features.map((f, i) => {
          const shap = Number(f.shap_value || 0)
          const isPositive = shap >= 0
          const pct = (Math.abs(shap) / maxAbs) * 48
          return (
            <div key={i} className="grid grid-cols-[110px_1fr_56px] gap-3 items-center">
              <div className="text-xs text-ink truncate" title={f.feature || f.name}>
                {shapLabel(f.feature || f.name)}
              </div>
              <div className="relative h-2 bg-line/40">
                <div className="absolute left-1/2 top-0 bottom-0 w-px bg-ink/30" />
                <div
                  className={isPositive ? 'absolute top-0 bottom-0 bg-accent' : 'absolute top-0 bottom-0 bg-ink/60'}
                  style={{
                    left: isPositive ? '50%' : `${50 - pct}%`,
                    width: `${pct}%`,
                  }}
                />
              </div>
              <div className={isPositive ? 'text-xs font-mono text-right text-accent' : 'text-xs font-mono text-right text-ink-muted'}>
                {isPositive ? '+' : ''}{shap.toFixed(2)}
              </div>
            </div>
          )
        })}
      </div>
      {baseValue != null && (
        <div className="mt-4 pt-3 border-t border-line/60 flex justify-between items-baseline">
          <span className="text-xs font-mono uppercase tracking-widest text-ink-subtle">Baseline model</span>
          <span className="text-xs font-mono text-ink-muted">{Number(baseValue).toFixed(1)}</span>
        </div>
      )}
    </div>
  )
}

function describeFeature(feature, value, impact) {
  const v = typeof value === 'number' ? value : Number(value) || 0
  const norm = feature && feature.startsWith('car_') && !feature.startsWith('car_rating_') && !feature.startsWith('car_is_')
    ? feature.slice(4)
    : feature
  switch (norm) {
    case 'car_is_electric':
      return 'Motorizare electrică'
    case 'car_is_hybrid':
      return 'Motorizare hibridă'
    case 'car_is_suv':
      return 'Caroserie SUV'
    case 'car_is_coupe':
      return 'Caroserie coupé'
    case 'car_is_sedan':
      return 'Caroserie sedan'
    case 'price_ratio':
      return 'Preț bun raportat la buget'
    case 'car_rating_siguranta':
      if (v >= 4.5) return `Siguranță excelentă (${v.toFixed(1)}/5)`
      if (v >= 3.5) return `Siguranță foarte bună (${v.toFixed(1)}/5)`
      return `Rating siguranță ${v.toFixed(1)}/5`
    case 'car_rating_comfort':
      if (v >= 4.5) return `Confort premium (${v.toFixed(1)}/5)`
      if (v >= 3.5) return `Confort foarte bun (${v.toFixed(1)}/5)`
      return `Rating confort ${v.toFixed(1)}/5`
    case 'car_rating_sport':
      if (v >= 4.5) return `Caracter sportiv puternic (${v.toFixed(1)}/5)`
      if (v >= 3.5) return `Performanță sportivă bună (${v.toFixed(1)}/5)`
      return `Rating sport ${v.toFixed(1)}/5`
    case 'car_rating_economie':
      if (v >= 4.5) return `Foarte economică (${v.toFixed(1)}/5)`
      if (v >= 3.5) return `Eficientă energetic (${v.toFixed(1)}/5)`
      return `Rating economie ${v.toFixed(1)}/5`
    case 'car_rating_estetica':
      if (v >= 4.5) return `Design remarcabil (${v.toFixed(1)}/5)`
      if (v >= 3.5) return `Design pe gustul tău (${v.toFixed(1)}/5)`
      return `Rating estetică ${v.toFixed(1)}/5`
    case 'pref_siguranta':
      return `Pui ${Math.round(v > 1 ? v : v * 100)}% accent pe siguranță`
    case 'pref_comfort':
      return `Pui ${Math.round(v > 1 ? v : v * 100)}% accent pe confort`
    case 'pref_sport':
      return `Pui ${Math.round(v > 1 ? v : v * 100)}% accent pe sport`
    case 'pref_economie':
      return `Pui ${Math.round(v > 1 ? v : v * 100)}% accent pe economie`
    case 'pref_estetica':
      return `Pui ${Math.round(v > 1 ? v : v * 100)}% accent pe design`
    case 'budget':
    case 'user_budget':
      return `Bugetul tău de ${Math.round(v).toLocaleString('ro-RO')} €`
    case 'pret':
    case 'price':
      return `Preț ${Math.round(v).toLocaleString('ro-RO')} €`
    case 'putere_cp':
      return `${Math.round(v)} CP sub capotă`
    case 'consum_mediu':
      return `Consum ${v.toFixed(1)} l/100km`
    case 'an':
      return `Model din ${Math.round(v)}`
    case 'numar_locuri':
      return `${Math.round(v)} locuri`
    case 'volum_portbagaj':
      return `Portbagaj ${Math.round(v)} L`
    case 'emisii_co2':
      return `Emisii ${Math.round(v)} g CO₂/km`
    case 'user_inaltime':
    case 'inaltime':
      return `Potrivit pentru înălțimea ta (${Math.round(v)} cm)`
    case 'user_greutate':
    case 'greutate':
      return `Potrivit pentru greutatea ta (${Math.round(v)} kg)`
    case 'km_zi':
      return `Pentru ${Math.round(v)} km/zi în medie`
    default: {
      const cleaned = (feature || '')
        .replace(/^car_rating_/, '')
        .replace(/^car_/, '')
        .replace(/^pref_/, '')
        .replace(/^user_/, '')
        .replace(/_/g, ' ')
      const cap = cleaned.charAt(0).toUpperCase() + cleaned.slice(1)
      return v ? `${cap} (${typeof v === 'number' ? v.toFixed(1) : v})` : cap
    }
  }
}

function isPositiveImpact(f) {
  if (f.impact === 'positive' || f.impact === 'pos') return true
  if (typeof f.impact === 'number' && f.impact > 0) return true
  if (typeof f.shap_value === 'number' && f.shap_value > 0) return true
  return false
}
function autovitUrl(marca, model) {
  const slug = (str) => (str || '').toString().toLowerCase().trim().replace(/\s+/g, '-')
  return `https://www.autovit.ro/autoturisme/${slug(marca)}/${slug(model)}`
}

function ProfileBar({ label, percent }) {
  return (
    <div className="flex-1 min-w-[140px]">
      <div className="flex justify-between items-baseline mb-2">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted">{label}</div>
        <div className="text-sm font-mono text-ink">{percent}%</div>
      </div>
      <div className="w-full h-1 bg-line">
        <div className="h-full bg-ink" style={{ width: `${percent}%` }} />
      </div>
    </div>
  )
}

export default function Recommendations() {
  const { user } = useAuth()
  const [recs, setRecs] = useState([])
  const [carDetails, setCarDetails] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [diversity, setDiversity] = useState(false)
  const [profile, setProfile] = useState(null)
  const [feedbackMap, setFeedbackMap] = useState({})
  const [feedbackBusy, setFeedbackBusy] = useState({})
  const [poolInfo, setPoolInfo] = useState({ candidates: null, total: null })
  const [recommendationId, setRecommendationId] = useState(null)
  const [sessionRating, setSessionRating] = useState(0)
  const [sessionComment, setSessionComment] = useState('')
  const [expandedShap, setExpandedShap] = useState({})
  const [sessionSubmitting, setSessionSubmitting] = useState(false)
  const [sessionSubmitted, setSessionSubmitted] = useState(false)
  const [availableBrands, setAvailableBrands] = useState([])
  const [selectedBrands, setSelectedBrands] = useState([])
  const [brandsExpanded, setBrandsExpanded] = useState(false)

  const toggleBrand = (marca) => {
    setSelectedBrands(prev =>
      prev.includes(marca) ? prev.filter(b => b !== marca) : [...prev, marca]
    )
  }

  useEffect(() => {
    loadRecommendations()
  }, [diversity, selectedBrands])

  useEffect(() => {
    loadFeedbackHistory()
  }, [])
  useEffect(() => {
    recommendationsApi.getBrands().then(setAvailableBrands).catch(() => {})
  }, [])

  async function loadRecommendations() {
    setLoading(true)
    setError(null)
    try {
      const data = await recommendationsApi.getFromProfile(diversity, selectedBrands)
      const list = data.recommendations || data.items || (Array.isArray(data) ? data : [])
      const prefs = data.profile || data.preferences || data.user_profile || null
      if (prefs) setProfile(prefs)
      setRecs(list)
      setPoolInfo({
        candidates: data.total_candidates ?? null,
        total: data.total_in_db ?? null,
      })
      setRecommendationId(data.session_id ?? data.recommendation_id ?? null)
      setSessionRating(0)
      setSessionComment('')
      setSessionSubmitted(false)

      const carIds = list.map(r => r.id).filter(Boolean)
      const details = {}
      await Promise.all(carIds.map(async (id) => {
        try {
          const car = await carsApi.getById(id)
          details[id] = car
        } catch (e) { /* skip */ }
      }))
      setCarDetails(details)
    } catch (err) {
      console.error('Recommendations failed:', err)
      const msg = err.response?.data?.detail || err.message || 'Eroare necunoscută'
      if (err.response?.status === 400 || /profil/i.test(String(msg))) {
        setError('profile_required')
      } else {
        setError(msg)
      }
    } finally {
      setLoading(false)
    }
  }

  async function loadFeedbackHistory() {
    try {
      const history = await feedbackApi.getHistory()
      const items = Array.isArray(history) ? history : (history.items || history.feedback || [])
      const map = {}
      items.forEach(fb => {
        const carId = fb.car_id
        if (!carId) return
        if (map[carId] !== undefined) return
        if (map[carId] !== undefined) return
        const r = fb.rating
        if (r === 1) map[carId] = 'like'
        else if (r === -1) map[carId] = 'dislike'
      })
      setFeedbackMap(map)
    } catch (err) {
      console.warn('Nu s-a putut incarca istoricul feedback:', err)
    }
  }

  async function handleFeedback(carId, type) {
    const prev = feedbackMap[carId]
    console.log('[FB] click', { carId, type, prev })
    const isToggleOff = prev === type
    const rating = isToggleOff ? 0 : (type === 'like' ? 1 : -1)
    setFeedbackMap(s => {
      const next = { ...s }
      if (isToggleOff) delete next[carId]
      else next[carId] = type
      return next
    })
    try {
      await feedbackApi.submit(carId, rating)
      console.log('[FB] saved', { carId, rating })
    } catch (err) {
      console.error('[FB] failed:', err.response?.data || err.message || err)
      setFeedbackMap(s => ({ ...s, [carId]: prev }))
      alert('Nu s-a putut salva feedback-ul.')
    }
  }

  async function submitSessionFeedback() {
    if (sessionRating < 1 || !recommendationId) return
    setSessionSubmitting(true)
    try {
      await recommendationsApi.submitSessionFeedback(
        recommendationId,
        sessionRating,
        sessionComment.trim() || null
      )
      setSessionSubmitted(true)
    } catch (err) {
      console.error('[Session FB] failed:', err.response?.data || err.message || err)
      alert('Nu s-a putut trimite evaluarea.')
    } finally {
      setSessionSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-20 text-center">
        <div className="text-sm font-mono uppercase tracking-widest text-ink-muted animate-pulse">
          se calculează recomandările...
        </div>
      </div>
    )
  }

  if (error === 'profile_required') {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20 text-center">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
          Profil incomplet
        </div>
        <h1 className="font-display text-4xl text-ink mb-6">
          Mai întâi <span className="italic">profilul tău</span>.
        </h1>
        <p className="text-ink-muted mb-8">
          Pentru recomandări personalizate, completează profilul ergonomic și mini-testul.
        </p>
        <Link to="/profile" className="px-6 py-3 bg-ink text-canvas inline-block hover:bg-accent transition">
          Completează profilul
        </Link>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-20 text-center">
        <p className="text-danger">{error}</p>
      </div>
    )
  }

  const axes = profile ? [
    { label: 'Confort', value: profile.comfort ?? profile.pref_comfort ?? 0 },
    { label: 'Sport', value: profile.sport ?? profile.pref_sport ?? 0 },
    { label: 'Siguranță', value: profile.siguranta ?? profile.pref_siguranta ?? 0 },
    { label: 'Economie', value: profile.economie ?? profile.pref_economie ?? 0 },
    { label: 'Estetică', value: profile.estetica ?? profile.pref_estetica ?? 0 },
  ].map(a => ({ ...a, percent: Math.round(a.value > 1 ? a.value : a.value * 100) })) : []

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      <div className="mb-12">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
          Recomandările tale · Top {recs.length}
        </div>
        <h1 className="font-display text-6xl tracking-tightest text-ink mb-6 leading-tight">
          Pentru <span className="italic text-accent">{user?.username || 'tine'}</span>.
        </h1>
        <p className="text-lg text-ink-muted max-w-2xl">
          Cele {recs.length} mașini care se potrivesc cel mai bine profilului tău. Pentru fiecare vezi motivele exacte și poți marca ce-ți place sau nu — recomandările viitoare se vor adapta.
        </p>
        {availableBrands.length > 0 && (
          <div className="mt-10 mb-8">
            <div className="flex items-center gap-4 mb-3">
              <button
                onClick={() => setBrandsExpanded(!brandsExpanded)}
                className="text-xs font-mono text-ink-muted tracking-wider hover:text-accent transition"
              >
                FILTREAZĂ DUPĂ MARCĂ{selectedBrands.length > 0 ? ` · ${selectedBrands.length} selectate` : ''} {brandsExpanded ? '−' : '+'}
              </button>
              {selectedBrands.length > 0 && (
                <button
                  onClick={() => setSelectedBrands([])}
                  className="text-xs text-ink-muted hover:text-accent transition"
                >
                  Șterge filtrul
                </button>
              )}
            </div>
            {brandsExpanded && (
              <div className="flex flex-wrap gap-2">
                {availableBrands.map(b => {
                  const isSelected = selectedBrands.includes(b.marca)
                  return (
                    <button
                      key={b.marca}
                      onClick={() => toggleBrand(b.marca)}
                      className={
                        isSelected
                          ? "px-3 py-1.5 border border-accent bg-accent text-white text-sm transition"
                          : "px-3 py-1.5 border border-line bg-surface text-ink text-sm hover:border-accent transition"
                      }
                    >
                      {b.marca} <span className="opacity-60 ml-1">{b.count}</span>
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        )}
        {poolInfo.candidates !== null && poolInfo.total !== null && (
          <p className="text-sm text-ink-muted mt-4 max-w-2xl">
            Sistemul a analizat <span className="font-mono text-ink">{poolInfo.candidates}</span> mașini compatibile cu {selectedBrands.length > 0 ? 'bugetul, combustibilul și mărcile selectate' : 'bugetul și combustibilul tău'}, din <span className="font-mono text-ink">{poolInfo.total}</span> mașini totale din catalog.
          </p>
        )}
      </div>

      {axes.length > 0 && (
        <div className="border border-line bg-surface p-6 mb-8">
          <div className="flex items-center justify-between mb-5 gap-4 flex-wrap">
            <div className="text-xs font-mono uppercase tracking-widest text-ink-muted">
              Profilul tău din mini-test
            </div>
            <Link to="/test" className="text-xs text-accent hover:underline whitespace-nowrap">
              Modifică răspunsurile →
            </Link>
          </div>
          <div className="flex gap-8 flex-wrap">
            {axes.map(axis => (
              <ProfileBar key={axis.label} label={axis.label} percent={axis.percent} />
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mb-6 text-sm">
        <div className="text-ink-muted">{recs.length} recomandări</div>
        <label className="flex items-center gap-3 cursor-pointer select-none">
          <span className="text-ink-muted">Recomandări diverse</span>
          <div className={`relative w-10 h-5 transition ${diversity ? 'bg-accent' : 'bg-line'}`}>
            <input
              type="checkbox"
              checked={diversity}
              onChange={(e) => setDiversity(e.target.checked)}
              className="opacity-0 absolute inset-0 cursor-pointer w-full h-full"
            />
            <div className={`absolute top-0.5 w-4 h-4 bg-canvas transition-all ${diversity ? 'left-5' : 'left-0.5'}`} />
          </div>
        </label>
      </div>

      <div className="space-y-6">
        {recs.map((rec, idx) => {
          const car = carDetails[rec.id] || {}
          const matchPct = Math.round(rec.score_total ?? rec.score ?? 0)
          const features = rec.score_details?.explanation?.top_features
            || rec.explanation?.top_features
            || []
          const positives = features.filter(isPositiveImpact).slice(0, 4)
          const fbState = feedbackMap[rec.id]
          const isBusy = !!feedbackBusy[rec.id]

          return (
            <div key={rec.id} className="border border-line bg-surface p-8 grid md:grid-cols-[1fr_2fr] gap-8">
              <div>
                <div className="text-xs font-mono uppercase tracking-widest text-accent mb-3 flex items-center gap-2">
                  <span>{String(idx + 1).padStart(2, '0')} · Recomandat</span>
                  {rec.score_details?.pinned_by_like && (
                    <span className="text-ink bg-accent/10 px-2 py-0.5">★ Îmi place</span>
                  )}
                </div>
                <h2 className="font-display text-4xl text-ink mb-1 tracking-tight">
                  <Link to={`/cars/${rec.id}`} className="hover:text-accent transition">
                    {rec.marca} {rec.model}
                  </Link>
                </h2>
                <div className="text-ink-muted mb-6">{rec.an}</div>
                <div className="font-mono text-3xl text-ink">
                  {Number(rec.pret).toLocaleString('ro-RO')} €
                </div>
              </div>

              <div>
                <div className="flex justify-between items-baseline mb-2">
                  <div className="text-xs font-mono uppercase tracking-widest text-ink-muted">
                    Potrivire cu profilul tău
                  </div>
                  <div className="font-mono text-2xl text-ink">{matchPct}%</div>
                </div>
                <div className="w-full h-1 bg-line mb-6">
                  <div className="h-full bg-accent transition-all" style={{ width: `${Math.min(100, Math.max(0, matchPct))}%` }} />
                </div>

                <div className="grid grid-cols-4 gap-4 mb-6 pb-6 border-b border-line">
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-ink-subtle mb-1">Combustibil</div>
                    <div className="text-sm text-ink capitalize">{rec.tip_combustibil || '—'}</div>
                  </div>
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-ink-subtle mb-1">Putere</div>
                    <div className="text-sm text-ink">{car.putere_cp ? `${car.putere_cp} CP` : '—'}</div>
                  </div>
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-ink-subtle mb-1">Consum</div>
                    <div className="text-sm text-ink">{car.consum_mediu ? `${car.consum_mediu} l/100km` : '—'}</div>
                  </div>
                  <div>
                    <div className="text-xs font-mono uppercase tracking-widest text-ink-subtle mb-1">Caroserie</div>
                    <div className="text-sm text-ink capitalize">{rec.tip_caroserie || '—'}</div>
                  </div>
                </div>

                <div className="mb-6">
                  <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-3">
                    De ce ți se potrivește
                  </div>
                  {positives.length > 0 ? (
                    <ul className="space-y-2">
                      {positives.map((f, i) => (
                        <li key={i} className="flex items-start gap-3 text-sm text-ink">
                          <span className="text-accent font-mono mt-0.5">+</span>
                          <span>{describeFeature(f.feature || f.name, f.value, f.impact)}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-ink-muted italic">Mașină echilibrată pe toate criteriile.</p>
                  )}
                </div>

                {features.length > 0 && (
                  <div className="mb-6">
                    <button
                      type="button"
                      onClick={() => setExpandedShap(prev => ({ ...prev, [rec.id]: !prev[rec.id] }))}
                      className="text-xs font-mono uppercase tracking-widest text-ink-muted hover:text-ink transition"
                    >
                      {expandedShap[rec.id] ? 'Ascunde' : 'Vezi'} analiza tehnică {expandedShap[rec.id] ? '↑' : '↓'}
                    </button>
                    {expandedShap[rec.id] && (
                      <ShapChart
                        features={features}
                        baseValue={rec.score_details?.explanation?.base_value ?? rec.explanation?.base_value}
                      />
                    )}
                  </div>
                )}
                <div className="flex gap-3 items-center">
                  <button
                    onClick={() => handleFeedback(rec.id, 'like')}
                    disabled={isBusy}
                    className={`px-5 py-2 text-sm border transition disabled:opacity-50 ${
                      fbState === 'like'
                        ? 'bg-ink text-canvas border-ink'
                        : 'border-line text-ink-muted hover:border-ink hover:text-ink'
                    }`}
                  >
                    {fbState === 'like' ? '✓ Îmi place' : 'Îmi place'}
                  </button>
                  <button
                    onClick={() => handleFeedback(rec.id, 'dislike')}
                    disabled={isBusy}
                    className={`px-5 py-2 text-sm border transition disabled:opacity-50 ${
                      fbState === 'dislike'
                        ? 'bg-ink text-canvas border-ink'
                        : 'border-line text-ink-muted hover:border-ink hover:text-ink'
                    }`}
                  >
                    {fbState === 'dislike' ? '✓ Nu-mi place' : 'Nu-mi place'}
                  </button>
                  <button
                    onClick={() => window.open(autovitUrl(rec.marca, rec.model), '_blank', 'noopener,noreferrer')}
                    className="ml-auto text-sm text-ink-muted hover:text-accent transition"
                  >
                    Vezi anunțuri →
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {recommendationId && (
        <div className="mt-12 border border-line bg-surface p-8">
          {sessionSubmitted ? (
            <div className="text-center py-6">
              <div className="text-xs font-mono uppercase tracking-widest text-accent mb-3">
                Multumim
              </div>
              <p className="text-ink text-lg">
                Evaluarea ta a fost trimisa. Ne ajuta sa imbunatatim modelul de recomandare.
              </p>
            </div>
          ) : (
            <>
              <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-4">
                Evaluare finala
              </div>
              <h2 className="font-display text-3xl text-ink mb-3 tracking-tight">
                Cum ti s-au parut aceste recomandari?
              </h2>
              <p className="text-ink-muted mb-6 max-w-2xl">
                Parerea ta ajuta sistemul sa devina mai precis. Folosim raspunsurile pentru a antrena modelul si a imbunatati recomandarile pentru toti utilizatorii.
              </p>
              <div className="flex gap-2 mb-6 items-center">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setSessionRating(star)}
                    aria-label={`${star} stele`}
                    className={`w-14 h-14 text-3xl border transition ${
                      star <= sessionRating
                        ? 'border-accent bg-accent/10 text-accent'
                        : 'border-line text-ink-subtle hover:border-ink/40 hover:text-ink'
                    }`}
                  >
                    {String.fromCharCode(9733)}
                  </button>
                ))}
                {sessionRating > 0 && (
                  <div className="ml-3 text-sm font-mono text-ink-muted">
                    {sessionRating}/5
                  </div>
                )}
              </div>
              <textarea
                value={sessionComment}
                onChange={(e) => setSessionComment(e.target.value)}
                placeholder="Comentariu (optional)..."
                rows={3}
                maxLength={1000}
                className="w-full border border-line bg-canvas px-4 py-3 text-ink placeholder:text-ink-subtle resize-none mb-4 focus:outline-none focus:border-ink transition"
              />
              <button
                onClick={submitSessionFeedback}
                disabled={sessionRating < 1 || sessionSubmitting}
                className="px-6 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition disabled:opacity-50"
              >
                {sessionSubmitting ? 'Se trimite...' : 'Trimite evaluarea'}
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}
