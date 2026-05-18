import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { profileApi } from '../../api/profile'

const FUEL_TYPES = [
  { value: 'benzina', label: 'Benzină' },
  { value: 'motorina', label: 'Motorină' },
  { value: 'hibrid', label: 'Hibrid' },
  { value: 'electric', label: 'Electric' },
]

const USAGE_CATEGORIES = [
  { value: 20, label: 'Rar', sub: 'Mai mult în oraș și pentru treburi zilnice' },
  { value: 40, label: 'Ocazional', sub: 'Câteva drumuri lungi pe lună' },
  { value: 70, label: 'Aproape în fiecare weekend', sub: 'Regular pe drumuri lungi' },
  { value: 100, label: 'Foarte des', sub: 'Drumurile lungi sunt parte din rutina mea' },
]

function findClosestUsage(kmZi) {
  if (kmZi == null || kmZi === '') return ''
  return USAGE_CATEGORIES.reduce((closest, cat) =>
    Math.abs(cat.value - kmZi) < Math.abs(closest.value - kmZi) ? cat : closest
  ).value
}

export default function Profile() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [serverError, setServerError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const { register, handleSubmit, formState: { errors }, watch, setValue, reset } = useForm({
    defaultValues: {
      inaltime: '',
      greutate: '',
      buget: '',
      km_zi: '',
      tip_combustibil: '',
    },
  })

  const selectedFuel = watch('tip_combustibil')
  const selectedUsage = watch('km_zi')

  useEffect(() => {
    async function load() {
      try {
        const profile = await profileApi.get()
        reset({
          inaltime: profile.inaltime ?? '',
          greutate: profile.greutate ?? '',
          buget: profile.buget ?? '',
          km_zi: findClosestUsage(profile.km_zi),
          tip_combustibil: profile.tip_combustibil ?? '',
        })
      } catch (err) {
        // Profil nou, formularul rămâne gol
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [reset])

  async function onSubmit(values) {
    setSubmitting(true)
    setServerError(null)
    try {
      const payload = {
        inaltime: parseInt(values.inaltime, 10),
        greutate: parseInt(values.greutate, 10),
        buget: parseInt(values.buget, 10),
        km_zi: parseInt(values.km_zi, 10),
        tip_combustibil: values.tip_combustibil,
      }
      await profileApi.update(payload)
      navigate('/recommendations', { replace: true })
    } catch (err) {
      const detail = err.response?.data?.detail
      setServerError(
        typeof detail === 'string'
          ? detail
          : 'Nu s-au putut salva datele. Verifică serverul și încearcă din nou.'
      )
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-32 text-center">
        <div className="text-sm text-ink-muted font-mono uppercase tracking-widest">
          se încarcă profilul...
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
        Pasul 3 din 4 · Date ergonomice
      </div>
      <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
        Aproape <span className="italic text-accent">gata</span>.
      </h1>
      <p className="text-ink-muted text-lg mb-12 max-w-xl leading-relaxed">
        Câteva date despre tine ca să găsim mașini care îți fac viața bună —
        nu doar pe hârtie.
      </p>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-10">
        {/* Înălțime + Greutate */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm text-ink mb-2">Înălțime</label>
            <div className="relative">
              <input
                type="number"
                inputMode="numeric"
                placeholder="180"
                className="w-full px-4 py-3 pr-12 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
                {...register('inaltime', {
                  required: 'Câmp obligatoriu',
                  valueAsNumber: true,
                  min: { value: 140, message: 'Minim 140 cm' },
                  max: { value: 220, message: 'Maxim 220 cm' },
                })}
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-mono text-ink-subtle">cm</span>
            </div>
            {errors.inaltime && <p className="text-sm text-danger mt-1">{errors.inaltime.message}</p>}
          </div>

          <div>
            <label className="block text-sm text-ink mb-2">Greutate</label>
            <div className="relative">
              <input
                type="number"
                inputMode="numeric"
                placeholder="75"
                className="w-full px-4 py-3 pr-12 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
                {...register('greutate', {
                  required: 'Câmp obligatoriu',
                  valueAsNumber: true,
                  min: { value: 40, message: 'Minim 40 kg' },
                  max: { value: 200, message: 'Maxim 200 kg' },
                })}
              />
              <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-mono text-ink-subtle">kg</span>
            </div>
            {errors.greutate && <p className="text-sm text-danger mt-1">{errors.greutate.message}</p>}
          </div>
        </div>

        {/* Buget */}
        <div>
          <label className="block text-sm text-ink mb-2">Buget</label>
          <div className="relative max-w-xs">
            <input
              type="number"
              inputMode="numeric"
              placeholder="30000"
              className="w-full px-4 py-3 pr-12 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
              {...register('buget', {
                required: 'Câmp obligatoriu',
                valueAsNumber: true,
                min: { value: 1000, message: 'Buget minim 1.000 €' },
                max: { value: 500000, message: 'Buget maxim 500.000 €' },
              })}
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-mono text-ink-subtle">€</span>
          </div>
          {errors.buget && <p className="text-sm text-danger mt-1">{errors.buget.message}</p>}
        </div>

        {/* Frecvența drumurilor lungi */}
        <div>
          <label className="block text-sm text-ink mb-3">
            Cât de des plănuiești drumuri lungi sau călătorii de weekend?
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {USAGE_CATEGORIES.map((cat) => {
              const isSelected = selectedUsage === cat.value
              return (
                <button
                  key={cat.value}
                  type="button"
                  onClick={() => setValue('km_zi', cat.value, { shouldValidate: true })}
                  className={`text-left px-5 py-4 border transition ${
                    isSelected
                      ? 'border-ink bg-ink/[0.03]'
                      : 'border-line hover:border-ink/40 bg-surface'
                  }`}
                >
                  <div className="font-medium text-ink mb-1">{cat.label}</div>
                  <div className="text-xs text-ink-muted leading-relaxed">{cat.sub}</div>
                </button>
              )
            })}
          </div>
          <input
            type="hidden"
            {...register('km_zi', { required: 'Alege un nivel de utilizare' })}
          />
          {errors.km_zi && <p className="text-sm text-danger mt-1">{errors.km_zi.message}</p>}
        </div>

        {/* Tip combustibil */}
        <div>
          <label className="block text-sm text-ink mb-3">Tip combustibil preferat</label>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {FUEL_TYPES.map((fuel) => {
              const isSelected = selectedFuel === fuel.value
              return (
                <button
                  key={fuel.value}
                  type="button"
                  onClick={() => setValue('tip_combustibil', fuel.value, { shouldValidate: true })}
                  className={`px-4 py-3 border text-sm transition ${
                    isSelected
                      ? 'border-ink bg-ink/[0.03] text-ink'
                      : 'border-line text-ink-muted hover:border-ink/40 hover:text-ink'
                  }`}
                >
                  {fuel.label}
                </button>
              )
            })}
          </div>
          <input
            type="hidden"
            {...register('tip_combustibil', { required: 'Alege un tip de combustibil' })}
          />
          {errors.tip_combustibil && <p className="text-sm text-danger mt-1">{errors.tip_combustibil.message}</p>}
        </div>

        {serverError && (
          <div className="border border-danger/30 bg-danger/5 text-danger text-sm px-4 py-3">
            {serverError}
          </div>
        )}

        <div className="flex items-center justify-between pt-6 border-t border-line gap-4">
          <p className="text-xs text-ink-subtle font-mono hidden sm:block">
            Datele rămân private. Folosite doar pentru recomandare.
          </p>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition disabled:opacity-50 ml-auto"
          >
            {submitting ? 'Se salvează...' : 'Vezi recomandările →'}
          </button>
        </div>
      </form>
    </div>
  )
}
