import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { carsApi } from '../../api/cars'
import { recommendationsApi } from '../../api/recommendations'
import { useAuth } from '../../context/AuthContext'
export default function Home() {
  const { user } = useAuth()
  const [totalCars, setTotalCars] = useState(null)
  const [totalBrands, setTotalBrands] = useState(null)
  useEffect(() => {
    async function loadStats() {
      try {
        const response = await carsApi.list({ per_page: 500, page: 1 })
        const items = Array.isArray(response)
          ? response
          : (response.items || response.cars || response.data || [])
        const total =
          response.total ??
          response.count ??
          response.total_count ??
          response.pagination?.total ??
          items.length
        if (total) setTotalCars(total)
        if (items.length > 0) {
          const allBrands = await recommendationsApi.getBrands()
          setTotalBrands(allBrands.length)
        }
      } catch (err) {
        console.warn('Nu s-au putut încărca statisticile:', err)
      }
    }
    loadStats()
  }, [])
  return (
    <div className="max-w-6xl mx-auto px-6 py-20">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
        Recomandări personalizate{totalCars ? ` · ${totalCars} de mașini` : ''}
      </div>
      <h1 className="font-display text-7xl tracking-tightest text-ink leading-[1.05] mb-12 max-w-4xl">
        Mașina potrivită,
        <br />
        <span className="italic text-accent">găsită științific.</span>
      </h1>
      <p className="text-xl text-ink-muted leading-relaxed mb-12 max-w-2xl">
        Răspunde la câteva întrebări despre tine — buget, înălțime, kilometraj
        zilnic, preferințe — și primești top 5 mașini care ți se potrivesc, cu
        motivele exacte pentru fiecare alegere.
      </p>
      <div className="flex flex-wrap gap-3 mb-24">
        <Link
          to={user ? '/test' : '/register'}
          className="px-8 py-4 bg-ink text-canvas text-base hover:bg-accent transition"
        >
          {user ? 'Începe recomandarea' : 'Creează cont'}
        </Link>
        <Link
          to="/catalog"
          className="px-8 py-4 bg-surface text-ink border border-line text-base hover:border-ink transition"
        >
          Vezi catalogul
        </Link>
      </div>
      <div className="border-t border-line pt-12 grid grid-cols-1 md:grid-cols-3 gap-12 mb-32">
        <div>
          <div className="font-display text-6xl text-ink mb-2 tracking-tight">
            {totalCars ?? '—'}
          </div>
          <div className="text-sm text-ink-muted">
            mașini selectate în catalog
          </div>
        </div>
        <div>
          <div className="font-display text-6xl text-ink mb-2 tracking-tight">
            {totalBrands ?? '—'}
          </div>
          <div className="text-sm text-ink-muted">
            mărci, de la economic la premium
          </div>
        </div>
        <div>
          <div className="font-display text-6xl text-ink mb-2 tracking-tight">5</div>
          <div className="text-sm text-ink-muted">
            recomandări la fiecare profil
          </div>
        </div>
      </div>
      <div>
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
          Cum funcționează
        </div>
        <h2 className="font-display text-5xl tracking-tightest text-ink mb-16 max-w-3xl leading-tight">
          Patru pași până la <span className="italic">mașina ta</span>.
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-16 gap-y-16">
          {[
            {
              n: '01',
              title: 'Mini-test',
              body: 'Răspunzi la 15 întrebări despre stilul tău de condus și ce contează pentru tine — siguranță, confort, sport, economie sau estetică.',
            },
            {
              n: '02',
              title: 'Profil ergonomic',
              body: 'Adaugi înălțime, greutate, buget, kilometraj zilnic și preferință de combustibil — datele care chiar contează când alegi o mașină.',
            },
            {
              n: '03',
              title: 'Top 5 recomandări',
              body: 'Un model de învățare automată combină profilul tău cu mașinile din catalog și alege cele 5 care ți se potrivesc cel mai bine, cu motive clare.',
            },
            {
              n: '04',
              title: 'Feedback care învață',
              body: 'Marchezi ce-ți place sau nu, iar recomandările viitoare se adaptează preferințelor tale reale — sistemul devine mai bun cu fiecare interacțiune.',
            },
          ].map(step => (
            <div key={step.n}>
              <div className="font-mono text-sm text-accent mb-3 tracking-widest">
                {step.n}
              </div>
              <h3 className="font-display text-2xl text-ink mb-3">{step.title}</h3>
              <p className="text-ink-muted leading-relaxed">{step.body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
