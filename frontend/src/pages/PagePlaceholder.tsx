import type { ReactNode } from 'react'

type PagePlaceholderProps = {
  title: string
  description: string
  icon: ReactNode
}

export default function PagePlaceholder({
  title,
  description,
  icon,
}: PagePlaceholderProps) {
  return (
    <section>
      <div className="mb-7">
        <p className="text-sm text-slate-500">Workspace / {title}</p>
      </div>
      <div className="flex min-h-[360px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center shadow-sm shadow-slate-200/40">
        <span className="mb-5 flex size-14 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
          {icon}
        </span>
        <h2 className="text-xl font-semibold tracking-tight text-slate-900">
          {title}
        </h2>
        <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
          {description}
        </p>
        <span className="mt-6 rounded-full bg-slate-100 px-3 py-1 text-[11px] font-medium text-slate-500">
          Coming soon
        </span>
      </div>
    </section>
  )
}
