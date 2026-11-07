import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/report-crisis': 'Report a Crisis',
  '/impact-analysis': 'Impact Analysis',
  '/recovery-simulator': 'Recovery Simulator',
  '/memory-centre': 'Memory Centre',
  '/decision-report': 'Decision Report',
  '/decision-replay': 'Decision Replay Lab',
}

export default function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { pathname } = useLocation()
  const title = pageTitles[pathname] ?? 'Dashboard'

  return (
    <div className="flex min-h-screen bg-slate-50">
      <div className="hidden shrink-0 lg:block">
        <Sidebar />
      </div>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 size-full cursor-default bg-slate-950/50"
            onClick={() => setMobileMenuOpen(false)}
            aria-label="Close navigation menu"
          />
          <div className="absolute inset-y-0 left-0 shadow-2xl">
            <Sidebar
              mobile
              onNavigate={() => setMobileMenuOpen(false)}
              onClose={() => setMobileMenuOpen(false)}
            />
          </div>
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar title={title} onMenuClick={() => setMobileMenuOpen(true)} />
        <main className="flex-1 p-4 sm:p-7 lg:p-9">
          <div className="mx-auto w-full max-w-[1440px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
