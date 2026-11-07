import type { ReactNode } from 'react'

export function SectionHeading({ title, subtitle, icon }: { title: string; subtitle: string; icon: ReactNode }) {
  return (
    <div className="flex items-start gap-3 border-b border-slate-100 px-5 py-4 sm:px-6">
      <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">{icon}</span>
      <div><h2 className="text-sm font-semibold text-slate-900">{title}</h2><p className="mt-1 text-xs leading-5 text-slate-500">{subtitle}</p></div>
    </div>
  )
}

export function Tag({ children, tone = 'slate' }: { children: ReactNode; tone?: 'slate' | 'blue' }) {
  return <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold ${tone === 'blue' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-600'}`}>{children}</span>
}

export function DemoBadge({ children = 'Illustrative demo data' }: { children?: string }) {
  return <span className="w-fit rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.1em] text-blue-700">{children}</span>
}
