import { useForm } from 'react-hook-form'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useState } from 'react'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [serverError, setServerError] = useState(null)

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm()

  async function onSubmit(values) {
    setServerError(null)
    try {
      await login(values.email, values.password)
      const redirectTo = location.state?.from?.pathname || '/test'
      navigate(redirectTo, { replace: true })
    } catch (err) {
      if (err.response?.status === 401) {
        setServerError('Email sau parolă incorectă.')
      } else if (err.response?.status === 429) {
        setServerError('Prea multe încercări. Așteaptă un minut și încearcă din nou.')
      } else {
        setServerError('A apărut o eroare. Verifică dacă serverul rulează.')
      }
    }
  }

  return (
    <div className="max-w-md mx-auto px-6 py-20">
      <div className="text-xs font-mono uppercase tracking-widest text-ink-muted mb-6">
        Cont existent
      </div>
      <h1 className="font-display text-5xl tracking-tight text-ink mb-3">
        Bine ai <span className="italic text-accent">revenit</span>.
      </h1>
      <p className="text-ink-muted mb-10">
        Conectează-te ca să continui de unde ai rămas.
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
          <label className="block text-sm text-ink mb-2">Parolă</label>
          <input
            type="password"
            autoComplete="current-password"
            className="w-full px-4 py-3 border border-line bg-surface text-ink focus:outline-none focus:border-ink transition"
            {...register('password', { required: 'Parola este obligatorie' })}
          />
          {errors.password && <p className="text-sm text-danger mt-1">{errors.password.message}</p>}
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
          {isSubmitting ? 'Se conectează...' : 'Conectează-te'}
        </button>
      </form>

      <p className="text-sm text-ink-muted mt-8">
        Nu ai cont încă?{' '}
        <Link to="/register" className="text-accent hover:underline">
          Crează unul acum
        </Link>
      </p>
    </div>
  )
}
