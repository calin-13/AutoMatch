import { useState, useMemo } from 'react'

const DEFAULTS = {
  avans: 5000,
  rataLunara: 400,
  luni: 60,
  dobandaAnuala: 8.5,
}

const PERIODS = [
  { value: 36, label: '3 ani' },
  { value: 48, label: '4 ani' },
  { value: 60, label: '5 ani' },
  { value: 72, label: '6 ani' },
  { value: 84, label: '7 ani' },
]

function calculateBudget({ avans, rataLunara, luni, dobandaAnuala }) {
  const r = (dobandaAnuala / 100) / 12
  if (r === 0) return avans + rataLunara * luni
  const pv = rataLunara * (1 - Math.pow(1 + r, -luni)) / r
  return avans + pv
}

export default function BudgetCalculatorModal({ open, onClose, onConfirm }) {
  const [values, setValues] = useState(DEFAULTS)

  const total = useMemo(() => {
    const avans = Number(values.avans) || 0
    const rataLunara = Number(values.rataLunara) || 0
    const luni = Number(values.luni) || 0
    const dobandaAnuala = Number(values.dobandaAnuala) || 0
    if (rataLunara <= 0 || luni <= 0) return avans
    return Math.round(calculateBudget({ avans, rataLunara, luni, dobandaAnuala }))
  }, [values])

  if (!open) return null

  function update(field, value) {
    setValues(prev => ({ ...prev, [field]: value }))
  }

  const totalValid = total >= 1000 && total <= 500000

  function handleConfirm() {
    if (totalValid) {
      onConfirm(total)
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={onClose}
    >
      <div
        className="bg-surface border border-line max-w-md w-full p-8 max-h-[90vh] overflow-y-auto"
        onClick={e => e.stopPropagation()}
      >
        <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-3">
          Calculator buget
        </div>
        <h2 className="font-display text-2xl text-ink mb-6">
          Cât îți poți permite?
        </h2>

        <div className="space-y-5">
          <div>
            <label className="block text-sm text-ink mb-2">Avans</label>
            <div className="relative">
              <input
                type="number"
                inputMode="numeric"
                value={values.avans}
                onChange={e => update('avans', e.target.value)}
                className="w-full px-4 py-3 pr-12 border border-line bg-canvas text-ink focus:outline-none focus:border-ink transition"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-mono text-ink-subtle">€</span>
            </div>
          </div>

          <div>
            <label className="block text-sm text-ink mb-2">Rată lunară dorită</label>
            <div className="relative">
              <input
                type="number"
                inputMode="numeric"
                value={values.rataLunara}
                onChange={e => update('rataLunara', e.target.value)}
                className="w-full px-4 py-3 pr-16 border border-line bg-canvas text-ink focus:outline-none focus:border-ink transition"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-mono text-ink-subtle">€/lună</span>
            </div>
          </div>

          <div>
            <label className="block text-sm text-ink mb-2">Perioada</label>
            <div className="grid grid-cols-5 gap-2">
              {PERIODS.map(p => (
                <button
                  key={p.value}
                  type="button"
                  onClick={() => update('luni', p.value)}
                  className={`py-2 text-sm border transition ${
                    values.luni === p.value
                      ? 'border-ink bg-ink/[0.03] text-ink'
                      : 'border-line text-ink-muted hover:border-ink/40'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm text-ink mb-2">Dobândă anuală</label>
            <div className="relative max-w-[160px]">
              <input
                type="number"
                step="0.1"
                inputMode="decimal"
                value={values.dobandaAnuala}
                onChange={e => update('dobandaAnuala', e.target.value)}
                className="w-full px-4 py-3 pr-10 border border-line bg-canvas text-ink focus:outline-none focus:border-ink transition"
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-mono text-ink-subtle">%</span>
            </div>
            <p className="text-xs text-ink-subtle mt-1">Medie credit auto RO ~8-10%</p>
          </div>

          <div className="pt-4 border-t border-line">
            <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-1">
              Buget total estimat
            </div>
            <div className="font-display text-3xl text-ink">
              {total.toLocaleString('ro-RO')} €
            </div>
            {!totalValid && (
              <p className="text-xs text-danger mt-2">
                Bugetul trebuie să fie între 1.000 € și 500.000 €
              </p>
            )}
          </div>
        </div>

        <div className="flex gap-3 pt-6 mt-4 border-t border-line">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 py-3 border border-line text-ink-muted hover:border-ink hover:text-ink transition"
          >
            Anulează
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={!totalValid}
            className="flex-1 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Setează ca buget
          </button>
        </div>
      </div>
    </div>
  )
}
