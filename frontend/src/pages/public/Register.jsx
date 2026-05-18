import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useState } from 'react'

export default function Register() {
  const { register: doRegister } = useAuth()
  const navigate = useNavigate()
  const [serverError, setServerError] = useState(null)

  const { register, handleSubmit, watch, formState: { errors, isSubmitting } } = useForm()
  const password = watch('password')

  async function onSubmit(values) {
    setServerError(null)
    try {
      await doRegister(values.email, values.username, values.password)
      navigate('/test', { replace: true })
    } catch (err) {
      const detail = err.response?.data?.detail
      if (err.response?.status === 400 || err.response?.status === 409) {
        setServerError(typeof detail === 'string' ? detail : 'Email sau username deja folosit.')
      } else {
        setServerError('A apărut o eroare. Verifică dacă serverul rulează.')
      }
    }
  }

  return (
    <div className="max-w-md mx-auto px-6 py-20">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
        Cont nou
      </div>
      <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
        Începe <span className="italic text-accent">acum</span>.
      </h1>
      <p className="text-ink-muted mb-10">
        Crează un cont și primești prima recomandare în câteva minute.
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

        <div>
          <label className="block text-sm text-ink mb-2">Nume utilizator</label>
          <input
            type="text"
            autoComplete="username"
            className="w-full px-4 py-3 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
            {...register('username', {
              required: 'Numele de utilizator este obligatoriu',
              minLength: { value: 3, message: 'Minim 3 caractere' },
              maxLength: { value: 30, message: 'Maxim 30 caractere' },
            })}
          />
          {errors.username && <p className="text-sm text-danger mt-1">{errors.username.message}</p>}
        </div>

        <div>
          <label className="block text-sm text-ink mb-2">Parolă</label>
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
            {...register('passwordConfirm', {
              required: 'Confirmă parola',
              validate: (v) => v === password || 'Parolele nu se potrivesc',
            })}
          />
          {errors.passwordConfirm && <p className="text-sm text-danger mt-1">{errors.passwordConfirm.message}</p>}
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
          {isSubmitting ? 'Se creează contul...' : 'Crează contul'}
        </button>
      </form>

      <p className="text-sm text-ink-muted mt-8">
        Ai deja cont?{' '}
        <Link to="/login" className="text-accent hover:underline">
          Conectează-te
        </Link>
      </p>
    </div>
  )
}
