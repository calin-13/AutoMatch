import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { testApi } from '../../api/test'

export default function Test() {
  const navigate = useNavigate()
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        const data = await testApi.getQuestions(2)
        setQuestions(data.questions || data || [])
        // Pre-completeaza raspunsurile din ultima submisie (daca exista)
        try {
          const responses = await testApi.getMyResponses()
          const latest = Array.isArray(responses)
            ? responses.find(r => r.version === 2)
            : null
          if (latest && Array.isArray(latest.answers)) {
            const map = {}
            latest.answers.forEach(a => {
              map[a.question_id] = a.option_id
            })
            setAnswers(map)
          }
        } catch (e) {
          // ignora - userul nu are raspunsuri vechi
        }
      } catch (err) {
        setError('Nu s-au putut încărca întrebările. Verifică dacă serverul rulează.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-32 text-center">
        <div className="text-sm text-ink-muted font-mono uppercase tracking-widest">
          se încarcă întrebările...
        </div>
      </div>
    )
  }

  if (error && questions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-32">
        <div className="border border-danger/30 bg-danger/5 text-danger px-4 py-3">
          {error}
        </div>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-32 text-center">
        <p className="text-ink-muted">Nu sunt întrebări disponibile momentan.</p>
      </div>
    )
  }

  const total = questions.length
  const current = questions[currentIndex]
  const selectedOptionId = answers[current.id]
  const isAnswered = selectedOptionId !== undefined
  const isLast = currentIndex === total - 1
  const progressPct = (Object.keys(answers).length / total) * 100

  function selectOption(optionId) {
    setAnswers({ ...answers, [current.id]: optionId })
  }

  function goNext() {
    if (currentIndex < total - 1) setCurrentIndex(currentIndex + 1)
  }

  function goBack() {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1)
  }

  async function submit() {
    setSubmitting(true)
    setError(null)
    try {
      const answersList = Object.entries(answers).map(([qid, oid]) => ({
        question_id: parseInt(qid, 10),
        option_id: parseInt(oid, 10),
      }))
      await testApi.submit(2, answersList)
      navigate('/profile', { replace: true })
    } catch (err) {
      setError('Nu s-au putut trimite răspunsurile. Încearcă din nou.')
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      {/* Progress */}
      <div className="mb-12">
        <div className="flex items-center justify-between text-xs font-mono uppercase tracking-widest text-ink-muted mb-3">
          <span>Întrebarea {currentIndex + 1} din {total}</span>
          <span>{Math.round(progressPct)}%</span>
        </div>
        <div className="h-1 bg-line overflow-hidden">
          <div
            className="h-full bg-accent transition-all duration-500 ease-out"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Question */}
      <h1 className="font-display text-4xl sm:text-5xl tracking-tight text-ink leading-tight mb-10">
        {current.text}
      </h1>

      {/* Options */}
      <div className="space-y-3 mb-12">
        {current.options.map((opt) => {
          const isSelected = selectedOptionId === opt.id
          return (
            <button
              key={opt.id}
              onClick={() => selectOption(opt.id)}
              className={`w-full text-left px-5 py-4 border transition ${
                isSelected
                  ? 'border-ink bg-ink/[0.03]'
                  : 'border-line hover:border-ink/40 bg-surface'
              }`}
            >
              <div className="flex items-center gap-4">
                <div
                  className={`w-4 h-4 rounded-full border-2 flex-shrink-0 transition ${
                    isSelected ? 'border-accent bg-accent' : 'border-ink-subtle'
                  }`}
                />
                <span className="text-ink">{opt.text}</span>
              </div>
            </button>
          )
        })}
      </div>

      {error && (
        <div className="border border-danger/30 bg-danger/5 text-danger text-sm px-4 py-3 mb-6">
          {error}
        </div>
      )}

      {/* Nav */}
      <div className="flex items-center justify-between pt-6 border-t border-line">
        <button
          onClick={goBack}
          disabled={currentIndex === 0}
          className="text-sm text-ink-muted hover:text-ink disabled:opacity-30 disabled:hover:text-ink-muted transition"
        >
          ← Înapoi
        </button>

        {isLast ? (
          <button
            onClick={submit}
            disabled={Object.keys(answers).length === 0 || submitting}
            className="px-6 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition disabled:opacity-50"
          >
            {submitting ? 'Se trimit...' : 'Trimite răspunsurile'}
          </button>
        ) : (
          <button
            onClick={goNext}
            className="px-6 py-3 bg-ink text-canvas font-medium hover:bg-ink/90 transition disabled:opacity-50"
          >
            Continuă →
          </button>
        )}
      </div>
    </div>
  )
}
