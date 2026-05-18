import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-24">
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-8">
          Recomandări personalizate · 198 de mașini
        </div>

        <h1 className="font-display text-7xl tracking-tightest text-ink leading-[0.95] mb-8 max-w-4xl">
          Mașina potrivită,<br />
          <span className="italic text-accent">găsită științific.</span>
        </h1>

        <p className="text-xl text-ink-muted max-w-2xl leading-relaxed mb-12">
          Răspunde la câteva întrebări despre tine — buget, înălțime, kilometraj
          zilnic, preferințe — și primești top 5 mașini care ți se potrivesc,
          cu motivele exacte pentru fiecare alegere.
        </p>

        <div className="flex flex-wrap gap-3">
          <Link
            to="/register"
            className="px-6 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition"
          >
            Începe recomandarea
          </Link>
          <Link
            to="/catalog"
            className="px-6 py-3 border border-line text-ink font-medium hover:border-ink transition"
          >
            Vezi catalogul
          </Link>
        </div>

        <div className="mt-24 pt-8 border-t border-line grid grid-cols-1 sm:grid-cols-3 gap-8">
          <div>
            <div className="text-5xl font-display text-ink mb-2 tracking-tight">198</div>
            <div className="text-sm text-ink-muted">mașini selectate în catalog</div>
          </div>
          <div>
            <div className="text-5xl font-display text-ink mb-2 tracking-tight">39</div>
            <div className="text-sm text-ink-muted">mărci de top, de la economic la premium</div>
          </div>
          <div>
            <div className="text-5xl font-display text-ink mb-2 tracking-tight">5</div>
            <div className="text-sm text-ink-muted">recomandări la fiecare profil</div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="border-t border-line bg-surface">
        <div className="max-w-6xl mx-auto px-6 py-24">
          <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
            Cum funcționează
          </div>
          <h2 className="font-display text-5xl tracking-tight text-ink mb-16 max-w-2xl">
            Patru pași până la <span className="italic">mașina ta</span>.
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            {[
              { n: '01', t: 'Profilul tău', d: 'Înălțime, greutate, buget și kilometraj zilnic — datele care contează pentru o recomandare onestă.' },
              { n: '02', t: 'Test rapid de stil', d: 'Cincisprezece întrebări despre confort, sport, siguranță, economie și design. Fără răspunsuri greșite.' },
              { n: '03', t: 'Selecție personalizată', d: 'Comparăm profilul tău cu fiecare mașină din catalog și păstrăm doar potrivirile reale.' },
              { n: '04', t: 'Top 5 cu motive', d: 'Pentru fiecare mașină primită, vezi clar de ce ți se potrivește și ce a contat cel mai mult.' },
            ].map((step) => (
              <div key={step.n}>
                <div className="text-xs font-mono text-accent mb-3">{step.n}</div>
                <h3 className="font-display text-2xl text-ink mb-3 tracking-tight">{step.t}</h3>
                <p className="text-sm text-ink-muted leading-relaxed">{step.d}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
