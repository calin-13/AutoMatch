import { useState, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import { recommendationsApi } from '../../api/recommendations'

export default function Layout() {
  const [stats, setStats] = useState({ total: null, brands: null })

  useEffect(() => {
    async function loadStats() {
      try {
        const brands = await recommendationsApi.getBrands()
        setStats({
          total: brands.reduce((sum, b) => sum + (b.count || 0), 0),
          brands: brands.length,
        })
      } catch (err) {
        // silent
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
