import React from 'react'
import { createRoot } from 'react-dom/client'
import IndexPage from './pages/index.jsx'
import './index.css'

function AppShell() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 backdrop-blur bg-white/70 border-b border-gray-100">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <img src="/logo.svg" alt="Logo" className="h-8 w-8 rounded" />
            <span className="text-lg font-semibold text-gray-900">AgriVision</span>
          </div>
          <a className="text-sm text-gray-600 hover:text-gray-900" href="#">Docs</a>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-8">
        <IndexPage />
      </main>
      <footer className="py-8 text-center text-xs text-gray-500">© {new Date().getFullYear()} AgriVision</footer>
    </div>
  )
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AppShell />
  </React.StrictMode>
)
