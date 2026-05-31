import { useState, useEffect } from 'react'
import { fetchCarImage } from '../utils/carImage'

const SILHOUETTES = {
  sedan: (
    <g>
      <path d="M 18 56 L 42 56 Q 54 34 84 32 L 156 32 Q 186 34 198 56 L 222 56" />
      <circle cx="60" cy="62" r="8" />
      <circle cx="180" cy="62" r="8" />
    </g>
  ),
  suv: (
    <g>
      <path d="M 18 56 L 38 56 Q 44 24 64 22 L 176 22 Q 196 24 202 56 L 222 56" />
      <circle cx="60" cy="62" r="10" />
      <circle cx="180" cy="62" r="10" />
    </g>
  ),
  hatchback: (
    <g>
      <path d="M 18 56 L 42 56 Q 52 36 76 34 L 132 34 L 158 38 Q 170 46 174 56 L 222 56" />
      <circle cx="60" cy="62" r="8" />
      <circle cx="180" cy="62" r="8" />
    </g>
  ),
  coupe: (
    <g>
      <path d="M 18 56 L 42 56 Q 56 30 90 28 L 122 28 Q 168 36 192 56 L 222 56" />
      <circle cx="60" cy="62" r="8" />
      <circle cx="180" cy="62" r="8" />
    </g>
  ),
  break: (
    <g>
      <path d="M 18 56 L 42 56 Q 52 34 76 32 L 196 32 Q 208 38 212 56 L 222 56" />
      <circle cx="60" cy="62" r="8" />
      <circle cx="180" cy="62" r="8" />
    </g>
  ),
}

export default function CarImagePlaceholder({ marca, model, an, tipCaroserie, tipCombustibil }) {
  const [imageUrl, setImageUrl] = useState(null)
  const [loaded, setLoaded] = useState(false)
  const [imgError, setImgError] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoaded(false)
    setImgError(false)
    fetchCarImage(marca, model).then(url => {
      if (!cancelled) {
        setImageUrl(url)
        setLoaded(true)
      }
    })
    return () => { cancelled = true }
  }, [marca, model])

  const silhouette = SILHOUETTES[(tipCaroserie || '').toLowerCase()] || SILHOUETTES.sedan
  const showImage = loaded && imageUrl && !imgError
  const showFallback = loaded && (!imageUrl || imgError)

  return (
    <div className="aspect-[16/7] bg-gradient-to-br from-ink/[0.015] via-canvas to-ink/[0.045] border border-line mb-12 relative overflow-hidden">
      {showImage && (
        <img
          src={imageUrl}
          alt={`${marca} ${model}`}
          className="absolute inset-0 w-full h-full object-contain"
          onError={() => setImgError(true)}
        />
      )}

      {showFallback && (
        <>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="font-display italic text-ink/[0.06] text-[8rem] sm:text-[12rem] md:text-[15rem] leading-none whitespace-nowrap">
              {marca}
            </div>
          </div>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <svg viewBox="0 0 240 80" className="w-1/2 max-w-[400px] text-ink/40" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round">
              {silhouette}
            </svg>
          </div>
        </>
      )}

      <div className="absolute top-5 left-6 text-xs font-mono uppercase tracking-widest text-ink-muted bg-canvas/85 backdrop-blur-sm px-2 py-1">
        {tipCaroserie} · {tipCombustibil}
      </div>
      <div className="absolute top-5 right-6 text-xs font-mono uppercase tracking-widest text-ink-muted bg-canvas/85 backdrop-blur-sm px-2 py-1">
        {an}
      </div>

      {showFallback && (
        <div className="absolute bottom-5 left-6 text-xs font-mono uppercase tracking-widest text-ink-subtle">
          Imagine reprezentativă
        </div>
      )}
    </div>
  )
}
