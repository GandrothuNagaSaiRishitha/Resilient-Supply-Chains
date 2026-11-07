import { Info } from 'lucide-react'
import type { ImpactAnalysis } from '../../types/impact'
import { isMockMode } from '../../services/apiConfig'

export default function ImpactAssumptions({
  assumptions,
}: Pick<ImpactAnalysis, 'assumptions'>) {
  return (
    <section className="rounded-2xl border border-blue-100 bg-blue-50/60 p-5 sm:p-6">
      <div className="flex items-start gap-3">
        <span className="flex size-9 shrink-0 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm shadow-blue-900/5">
          <Info size={18} />
        </span>
        <div>
          <h2 className="text-sm font-semibold text-slate-900">About these estimates</h2>
          <p className="mt-1 text-xs leading-5 text-slate-600">
            {isMockMode
              ? 'Illustrative demo analysis only. These values are not calculated from live operations or a backend service.'
              : 'These estimates are calculated from organization-scoped incident, purchase-order, supplier, and inventory records.'}
          </p>
        </div>
      </div>
      <ul className="mt-4 grid gap-2 pl-12 text-[11px] leading-5 text-slate-600 sm:grid-cols-2">
        {assumptions.items.map((assumption) => (
          <li key={assumption} className="relative pr-3 before:absolute before:-left-3 before:top-2 before:size-1 before:rounded-full before:bg-blue-400">
            {assumption}
          </li>
        ))}
      </ul>
    </section>
  )
}
