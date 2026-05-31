import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { useState } from 'react'
import { authApi } from '../../api/auth'

export default function ForgotPassword() {
  const [sent, setSent] = useState(false)
  const [serverError, setServerError] = useState(null)
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm()

  async function onSubmit(values) {
    setServerError(null)
    try {
      await authApi.forgotPassword(values.email)
      setSent(true)
    } catch (err) {
      if (err.response?.status === 429) {
        setServerError('Prea multe încercări. Așteaptă un minut și încearcă din nou.')
      } else {
        setServerError('A apărut o eroare. Verifică dacă serverul rulează.')
      }
    }
  }

  return (
    <div className="max-w-md mx-auto px-6 py-20">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
        Recuperare cont
      </div>
      <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
        Ai uitat <span className="italic text-accent">parola</span>?
      </h1>
      {sent ? (
        <div className="mt-6">
          <p className="text-ink-muted mb-6">
            Dacă există un cont cu acest email, ai primit un link de resetare.
            Verifică inbox-ul (și folderul spam). Linkul expiră în 30 de minute.
          </p>
          <Link to="/login" className="text-accent hover:underline text-sm">
            Înapoi la conectare
          </Link>
        </div>
      ) : (
        <>
          <p className="text-ink-muted mb-10">
            Introdu adresa de email și îți trimitem un link pentru a seta o parolă nouă.
          </p>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-sm text-ink mb-2">Email</label>
              <input
                type="email"
                autoComplete="email"
                className="w-full px-4 py-3 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
                {...register('email', {
                  required: 'Email-ul este obligatoriu',
                  pattern: { value: /^\S+@\S+\.\S+$/, message: 'Format email invalid' },
                })}
              />
              {errors.email && <p className="text-sm text-danger mt-1">{errors.email.message}</p>}
            </div>
            {serverError && (
              <div className="border border-danger/30 bg-danger/5 text-danger text-sm px-4 py-3">
                {serverError}
              </div>
            )}
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-6 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition disabled:opacity-50"
            >
              {isSubmitting ? 'Se trimite...' : 'Trimite link de resetare'}
            </button>
          </form>
          <p className="text-sm text-ink-muted mt-8">
            Ți-ai amintit parola?{' '}
            <Link to="/login" className="text-accent hover:underline">
              Conectează-te
            </Link>
          </p>
        </>
      )}
    </div>
  )
}
