import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from 'recharts'
import AdminNav from '../../components/layout/AdminNav'
import { adminApi } from '../../api/admin'

function StatCard({ label, value, sublabel }) {
  return (
    <div className="border border-line bg-surface p-6">
      <div className="text-xs text-ink-muted uppercase tracking-wider mb-2">{label}</div>
      <div className="text-4xl font-display text-ink tracking-tight">
        {value ?? '—'}
      </div>
      {sublabel && <div className="text-xs text-ink-subtle mt-1 font-mono">{sublabel}</div>}
    </div>
  )
}

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null
  return (
    <div className="bg-ink text-canvas px-3 py-2 text-xs font-mono">
      <div className="text-canvas/60 mb-1">{label}</div>
      <div>{typeof payload[0].value === 'number' ? payload[0].value.toFixed(3) : payload[0].value}</div>
    </div>
  )
}

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [featureImportance, setFeatureImportance] = useState(null)
  const [comparison, setComparison] = useState(null)
  const [mlMetrics, setMlMetrics] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const results = await Promise.allSettled([
        adminApi.getStats(),
        adminApi.getFeatureImportance(),
        adminApi.getModelComparison(),
        adminApi.getMLMetrics(),
      ])
      if (results[0].status === 'fulfilled') setStats(results[0].value)
      if (results[1].status === 'fulfilled') setFeatureImportance(results[1].value)
      if (results[2].status === 'fulfilled') setComparison(results[2].value)
      if (results[3].status === 'fulfilled') setMlMetrics(results[3].value)
      setLoading(false)
    }
    load()
  }, [])

  if (loading) {
    return (
      <>
        <AdminNav />
        <div className="max-w-6xl mx-auto px-6 pb-32 text-center">
          <div className="text-sm text-ink-muted font-mono uppercase tracking-widest animate-pulse">
            se încarcă datele admin...
          </div>
        </div>
      </>
    )
  }

  let featureChartData = []
  if (featureImportance) {
    const arr = Array.isArray(featureImportance)
      ? featureImportance
      : featureImportance.features || featureImportance.feature_importance || []
    featureChartData = arr
      .slice(0, 12)
      .map((f) => ({
        name: f.feature || f.name || f.key || 'unknown',
        importance: Number(f.importance ?? f.value ?? f.score ?? 0),
      }))
      .filter(d => d.importance > 0)
  }

  let comparisonData = []
  if (comparison) {
    const arr = comparison.regression || comparison.models || (Array.isArray(comparison) ? comparison : [])
    if (Array.isArray(arr)) {
      comparisonData = arr.map((m) => ({
        name: m.name || m.model || m.algorithm || 'unknown',
        r2: Number(m.r2 ?? m.r2_score ?? m.score ?? 0),
      })).filter(d => d.r2 > 0)
    }
  }

  const datasetSize = mlMetrics?.dataset?.size || mlMetrics?.dataset_size || 272

  return (
    <>
      <AdminNav />
      <div className="max-w-6xl mx-auto px-6 pb-12">
        <div className="mb-12">
          <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
            Admin · Dashboard
          </div>
          <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
            În spatele <span className="italic text-accent">algoritmului</span>.
          </h1>
          <p className="text-ink-muted text-lg max-w-2xl">
            Metrici platformă, performanța modelelor de învățare automată
            și interpretarea factorilor de decizie.
          </p>
        </div>

        {stats && (
          <div className="mb-16">
            <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
              Activitate platformă
            </div>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard label="Utilizatori" value={stats.total_users ?? stats.users_count ?? stats.users} />
              <StatCard label="Recomandări" value={stats.total_recommendations ?? stats.recommendations_count ?? stats.recommendations} />
              <StatCard label="Feedback-uri" value={stats.total_feedback ?? stats.feedback_count ?? stats.feedbacks} />
              <StatCard label="Mașini în catalog" value={stats.total_cars ?? datasetSize} />
            </div>
          </div>
        )}

        {featureChartData.length > 0 && (
          <div className="mb-16">
            <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-2">
              Învățare automată
            </div>
            <h2 className="font-display text-3xl tracking-tight text-ink mb-2">
              Cele mai <span className="italic">influente</span> caracteristici.
            </h2>
            <p className="text-sm text-ink-muted mb-8 max-w-xl">
              Importanța relativă a fiecărei caracteristici în deciziile modelului.
              Cu cât bara e mai lungă, cu atât caracteristica contribuie mai mult la scor.
            </p>
            <div className="border border-line bg-surface p-6">
              <ResponsiveContainer width="100%" height={Math.max(320, featureChartData.length * 32)}>
                <BarChart
                  data={featureChartData}
                  layout="vertical"
                  margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" horizontal={false} />
                  <XAxis type="number" stroke="#a8a29e" fontSize={11} tick={{ fontFamily: 'JetBrains Mono' }} />
                  <YAxis type="category" dataKey="name" stroke="#57534e" fontSize={12} width={130} tick={{ fontFamily: 'DM Sans' }} />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                  <Bar dataKey="importance" fill="#991b1b" radius={[0, 2, 2, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {comparisonData.length > 0 && (
          <div className="mb-16">
            <h2 className="font-display text-3xl tracking-tight text-ink mb-2">
              Modele <span className="italic">comparate</span>.
            </h2>
            <p className="text-sm text-ink-muted mb-8 max-w-xl">
              Performanța relativă a algoritmilor încercați. R² mai aproape
              de 1 înseamnă predicție mai precisă.
            </p>
            <div className="border border-line bg-surface p-6">
              <ResponsiveContainer width="100%" height={360}>
                <BarChart data={comparisonData} margin={{ top: 20, right: 30, left: 10, bottom: 50 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" vertical={false} />
                  <XAxis dataKey="name" stroke="#57534e" fontSize={11} tick={{ fontFamily: 'DM Sans' }} angle={-20} textAnchor="end" height={60} />
                  <YAxis stroke="#a8a29e" fontSize={11} domain={[0, 1]} tick={{ fontFamily: 'JetBrains Mono' }} />
                  <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
                  <Bar dataKey="r2" fill="#0c0a09" radius={[2, 2, 0, 0]} name="R²" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {featureChartData.length === 0 && comparisonData.length === 0 && (
          <div className="border border-line bg-surface p-8 text-center">
            <p className="text-ink-muted text-sm">
              Metricile ML încă nu sunt disponibile.
            </p>
          </div>
        )}
      </div>
    </>
  )
}
