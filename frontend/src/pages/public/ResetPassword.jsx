import { useForm } from 'react-hook-form'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useState } from 'react'
import { authApi } from '../../api/auth'

export default function ResetPassword() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const navigate = useNavigate()
  const [serverError, setServerError] = useState(null)
  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm()

  async function onSubmit(values) {
    setServerError(null)
    try {
      await authApi.resetPassword(token, values.password)
      navigate('/login', { replace: true, state: { reset: true } })
    } catch (err) {
      if (err.response?.status === 400) {
        setServerError('Linkul de resetare este invalid sau a expirat. Cere unul nou.')
      } else if (err.response?.status === 429) {
        setServerError('Prea multe încercări. Așteaptă un minut și încearcă din nou.')
      } else {
        setServerError('A apărut o eroare. Verifică dacă serverul rulează.')
      }
    }
  }

  if (!token) {
    return (
      <div className="max-w-md mx-auto px-6 py-20">
        <h1 className="font-display text-4xl tracking-tight text-ink mb-3">Link invalid</h1>
        <p className="text-ink-muted mb-6">Linkul de resetare nu conține un token valid.</p>
        <Link to="/forgot-password" className="text-accent hover:underline text-sm">
          Cere un link nou
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto px-6 py-20">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
        Parolă nouă
      </div>
      <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
        Setează o parolă <span className="italic text-accent">nouă</span>.
      </h1>
      <p className="text-ink-muted mb-10">Alege o parolă pe care nu ai mai folosit-o.</p>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <div>
          <label className="block text-sm text-ink mb-2">Parolă nouă</label>
          <input
            type="password"
            autoComplete="new-password"
            className="w-full px-4 py-3 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
            {...register('password', {
              required: 'Parola este obligatorie',
              minLength: { value: 6, message: 'Minim 6 caractere' },
            })}
          />
          {errors.password && <p className="text-sm text-danger mt-1">{errors.password.message}</p>}
        </div>
        <div>
          <label className="block text-sm text-ink mb-2">Confirmă parola</label>
          <input
            type="password"
            autoComplete="new-password"
            className="w-full px-4 py-3 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
            {...register('confirm', {
              required: 'Confirmă parola',
              validate: (v) => v === watch('password') || 'Parolele nu coincid',
            })}
          />
          {errors.confirm && <p className="text-sm text-danger mt-1">{errors.confirm.message}</p>}
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
          {isSubmitting ? 'Se salvează...' : 'Salvează parola nouă'}
        </button>
      </form>
      <p className="text-sm text-ink-muted mt-8">
        <Link to="/login" className="text-accent hover:underline">Înapoi la conectare</Link>
      </p>
    </div>
  )
}
