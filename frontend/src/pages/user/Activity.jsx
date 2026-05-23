import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { recommendationsApi } from '../../api/recommendations'
import { feedbackApi } from '../../api/feedback'

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('ro-RO', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function PreferencesSummary({ summary }) {
  function getCategory(...keys) {
    for (const k of keys) {
      if (summary?.[k]) {
        const data = summary[k]
        if (Array.isArray(data)) return data
        return Object.entries(data).map(([name, stats]) => ({
          name,
          likes: stats?.likes ?? 0,
          dislikes: stats?.dislikes ?? 0,
          net: stats?.net ?? (stats?.likes ?? 0) - (stats?.dislikes ?? 0),
        }))
      }
    }
    return []
  }

  const categories = [
    { title: 'Mărci', data: getCategory('by_brand', 'brands', 'brand') },
    { title: 'Caroserii', data: getCategory('by_bodytype', 'body_types', 'bodytype') },
    { title: 'Combustibili', data: getCategory('by_fuel', 'fuel_types', 'fuel') },
  ]

  const hasData = categories.some(c => c.data.length > 0)
  if (!hasData) return null

  return (
    <section className="mb-16 border border-line bg-surface p-6">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
        Preferințele tale agregate
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {categories.map(cat => {
          const sorted = [...cat.data].sort((a, b) => b.net - a.net)
          const topPositive = sorted.filter(d => d.net > 0).slice(0, 3)
          const topNegative = sorted.filter(d => d.net < 0).slice(0, 2)
          return (
            <div key={cat.title}>
              <div className="text-xs text-ink-muted uppercase tracking-wider mb-3">
                {cat.title}
              </div>
              {topPositive.length === 0 && topNegative.length === 0 ? (
                <p className="text-xs text-ink-subtle italic">Date insuficiente</p>
              ) : (
                <div className="space-y-2">
                  {topPositive.map(item => (
                    <div key={item.name} className="text-sm flex items-baseline justify-between">
                      <span className="text-ink capitalize">{item.name}</span>
                      <span className="text-accent font-mono text-xs">+{item.net}</span>
                    </div>
                  ))}
                  {topNegative.map(item => (
                    <div key={item.name} className="text-sm flex items-baseline justify-between">
                      <span className="text-ink-muted capitalize">{item.name}</span>
                      <span className="text-ink-subtle font-mono text-xs">{item.net}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}

export default function Activity() {
  const [recommendations, setRecommendations] = useState([])
  const [feedbacks, setFeedbacks] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const results = await Promise.allSettled([
          recommendationsApi.getHistory(),
          feedbackApi.getHistory(),
          feedbackApi.getSummary(),
        ])

        try {
          if (results[0].status === 'fulfilled' && results[0].value) {
            const d = results[0].value
            setRecommendations(d?.recommendations || d?.items || (Array.isArray(d) ? d : []))
          } else if (results[0].status === 'rejected') {
            console.error('history error:', results[0].reason)
          }
        } catch (e) { console.error('recommendations parse:', e) }

        try {
          if (results[1].status === 'fulfilled' && results[1].value) {
            const d = results[1].value
            setFeedbacks(d?.feedbacks || d?.items || (Array.isArray(d) ? d : []))
          } else if (results[1].status === 'rejected') {
            console.error('feedback history error:', results[1].reason)
          }
        } catch (e) { console.error('feedback parse:', e) }

        try {
          if (results[2].status === 'fulfilled' && results[2].value) {
            setSummary(results[2].value)
          } else if (results[2].status === 'rejected') {
            console.error('summary error:', results[2].reason)
          }
        } catch (e) { console.error('summary parse:', e) }
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-6 py-32 text-center">
        <div className="text-sm text-ink-muted font-mono uppercase tracking-widest">
          se încarcă activitatea...
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-12">
      <div className="mb-12">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-4">
          Activitatea ta
        </div>
        <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
          Ce ai <span className="italic text-accent">făcut</span> aici.
        </h1>
        <p className="text-ink-muted text-lg max-w-xl">
          Sesiuni de recomandări, mașinile pe care le-ai marcat, și preferințele
          tale agregate.
        </p>
      </div>

      {summary && <PreferencesSummary summary={summary} />}

      <section className="mb-16">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
          Sesiuni recente de recomandări
        </div>
        {recommendations.length === 0 ? (
          <p className="text-sm text-ink-muted">
            Nu ai încă sesiuni salvate. <Link to="/recommendations" className="text-accent hover:underline">Generează recomandări</Link> ca să apară aici.
          </p>
        ) : (
          <div className="space-y-3">
            {recommendations.slice(0, 10).map((rec) => {
              const topCar = rec.top_car || rec.car || (rec.items?.[0]) || null
              const carId = topCar?.id ?? topCar?.car_id
              return (
                <div key={rec.id} className="border border-line bg-surface px-5 py-4 flex items-center justify-between gap-4">
                  <div>
                    <div className="text-xs font-mono text-ink-muted mb-1">
                      {formatDate(rec.created_at)}
                    </div>
                    {topCar ? (
                      <div className="text-sm text-ink">
                        Top: <span className="font-medium">{topCar.marca} {topCar.model}</span>
                        {rec.items_count && (
                          <span className="text-ink-muted"> · {rec.items_count} recomandări</span>
                        )}
                      </div>
                    ) : (
                      <div className="text-sm text-ink-muted">Sesiune #{rec.id}</div>
                    )}
                  </div>
                  {carId && (
                    <Link to={`/cars/${carId}`} className="text-sm text-ink-muted hover:text-accent transition flex-shrink-0">
                      Vezi →
                    </Link>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </section>

      <section>
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
          Tot feedback-ul tău
        </div>
        {feedbacks.length === 0 ? (
          <p className="text-sm text-ink-muted">
            Încă n-ai marcat nicio mașină.
          </p>
        ) : (
          <div className="space-y-3">
            {feedbacks.slice(0, 20).map((fb) => {
              const car = fb.car || fb
              const carId = car?.id || fb?.car_id
              const carName = (car?.marca && car?.model) ? `${car.marca} ${car.model}` : `Mașina #${carId}`
              const rating = fb.rating
              return (
                <div key={fb.id} className="border border-line bg-surface px-5 py-4 flex items-center justify-between gap-4">
                  <div>
                    <div className="text-xs font-mono text-ink-muted mb-1">
                      {formatDate(fb.created_at)}
                    </div>
                    {carId ? (
                      <Link to={`/cars/${carId}`} className="text-sm text-ink hover:text-accent transition font-medium">
                        {carName}
                      </Link>
                    ) : (
                      <span className="text-sm text-ink font-medium">{carName}</span>
                    )}
                  </div>
                  <div className="flex-shrink-0">
                    {rating === 1 && <span className="text-xs font-mono uppercase tracking-widest text-accent">Îmi place</span>}
                    {rating === -1 && <span className="text-xs font-mono uppercase tracking-widest text-ink-muted">Nu-mi place</span>}
                    {(rating === 0 || rating == null) && <span className="text-xs font-mono uppercase tracking-widest text-ink-subtle">Neutru</span>}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}
