import {
  Activity,
  Brain,
  ChartNoAxesCombined,
  ClipboardList,
  FileText,
  LayoutDashboard,
  RotateCcw,
  Waves,
  X,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navigation = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { label: 'Report a Crisis', path: '/report-crisis', icon: ClipboardList },
  { label: 'Impact Analysis', path: '/impact-analysis', icon: ChartNoAxesCombined },
  { label: 'Recovery Simulator', path: '/recovery-simulator', icon: Activity },
  { label: 'Memory Centre', path: '/memory-centre', icon: Brain },
  { label: 'Decision Report', path: '/decision-report', icon: FileText },
  { label: 'Decision Replay Lab', path: '/decision-replay', icon: RotateCcw },
]

type SidebarProps = {
  mobile?: boolean
  onNavigate?: () => void
  onClose?: () => void
}

export default function Sidebar({
  mobile = false,
  onNavigate,
  onClose,
}: SidebarProps) {
  return (
    <aside className="flex h-full w-72 flex-col bg-[#101c36] text-slate-300">
      <div className="flex h-[76px] items-center justify-between border-b border-white/10 px-6">
        <NavLink
          to="/dashboard"
          onClick={onNavigate}
          className="flex items-center gap-3"
          aria-label="SHOCKWAVE AI home"
        >
          <span className="flex size-9 items-center justify-center rounded-xl bg-blue-500 text-white shadow-lg shadow-blue-950/30">
            <Waves size={19} strokeWidth={2.2} />
          </span>
          <span className="text-sm font-bold tracking-[0.13em] text-white">
            SHOCKWAVE <span className="text-blue-400">AI</span>
          </span>
        </NavLink>
        {mobile && (
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
            aria-label="Close navigation"
          >
            <X size={20} />
          </button>
        )}
      </div>

      <div className="px-4 pt-8">
        <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">
          Workspace
        </p>
        <nav className="space-y-1" aria-label="Main navigation">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              onClick={onNavigate}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-[13px] font-medium transition ${
                  isActive
                    ? 'bg-blue-500/15 text-blue-300 ring-1 ring-inset ring-blue-400/20'
                    : 'text-slate-400 hover:bg-white/5 hover:text-slate-100'
                }`
              }
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="mt-auto p-4">
        <div className="rounded-xl border border-white/10 bg-white/[0.04] p-4">
          <div className="mb-2 flex items-center gap-2">
            <span className="size-2 rounded-full bg-emerald-400" />
            <p className="text-xs font-medium text-slate-200">Systems operational</p>
          </div>
          <p className="text-[11px] leading-5 text-slate-500">
            Intelligence feeds are up to date.
          </p>
        </div>
        <p className="px-1 pt-4 text-[10px] text-slate-600">SHOCKWAVE AI · 1.0</p>
      </div>
    </aside>
  )
}
