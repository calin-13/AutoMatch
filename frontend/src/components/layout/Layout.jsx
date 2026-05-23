import { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import { carsApi } from '../../api/cars'

export default function Layout() {
  const [stats, setStats] = useState({ total: null, brands: null })

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
        const brands = items.length > 0
          ? new Set(items.map(c => c.marca).filter(Boolean)).size
          : null
        setStats({ total, brands })
      } catch (err) {
        // silent fail — footer arata —
      }
    }
    loadStats()
  }, [])

  return (
    <div className="min-h-screen flex flex-col bg-canvas">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-line mt-20 py-8">
        <div className="max-w-6xl mx-auto px-6 flex justify-between items-center flex-wrap gap-4">
          <div className="text-xs font-mono uppercase tracking-widest text-ink-muted">
            AutoMatch · 2026
          </div>
          <div className="text-xs font-mono uppercase tracking-widest text-ink-muted">
            {stats.total ?? '—'} mașini · {stats.brands ?? '—'} mărci
          </div>
        </div>
      </footer>
    </div>
  )
}
