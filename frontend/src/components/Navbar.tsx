import { Menu } from 'lucide-react'
import { dataSource } from '../services/apiConfig'

type NavbarProps = {
  title: string
  onMenuClick: () => void
}

export default function Navbar({ title, onMenuClick }: NavbarProps) {
  return (
    <header className="flex h-[76px] shrink-0 items-center justify-between border-b border-slate-200/80 bg-white px-4 sm:px-7 lg:px-9">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 lg:hidden"
          aria-label="Open navigation"
        >
          <Menu size={20} />
        </button>
        <h1 className="text-lg font-semibold tracking-tight text-slate-900 sm:text-xl">
          {title}
        </h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        <span className={`hidden rounded-full px-2.5 py-1 text-[9px] font-bold uppercase tracking-wide sm:inline-flex ${dataSource === 'mock' ? 'bg-amber-50 text-amber-700' : 'bg-emerald-50 text-emerald-700'}`}>
          {dataSource === 'mock' ? 'Mock data source' : 'API data source'}
        </span>
      </div>
    </header>
  )
}
