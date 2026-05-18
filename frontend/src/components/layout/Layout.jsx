import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-canvas">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t border-line py-8">
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between text-xs text-ink-muted font-mono uppercase tracking-widest">
          <span>AutoMatch · 2026</span>
          <span>198 mașini · 39 mărci</span>
        </div>
      </footer>
    </div>
  )
}
