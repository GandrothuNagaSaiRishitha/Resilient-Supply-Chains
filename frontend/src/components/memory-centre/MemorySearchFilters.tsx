import { ChevronDown, Filter, RotateCcw } from 'lucide-react'
import type { ReactNode } from 'react'
import type { CrisisType } from '../../types/crisisReport'
import type { MemoryCentreData, MemoryFilters, MemoryOutcome } from '../../types/memory'

const inputClassName =
  'w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-700 outline-none transition focus:border-blue-400 focus:ring-4 focus:ring-blue-500/10'

type Props = {
  data: MemoryCentreData
  filters: MemoryFilters
  onFilter: <K extends keyof MemoryFilters>(key: K, value: MemoryFilters[K]) => void
  onReset: () => void
}

export default function MemorySearchFilters({ data, filters, onFilter, onReset }: Props) {
  return (
    <section className="mb-5 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-200/40 sm:p-5">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2"><Filter size={16} className="text-slate-500" /><h2 className="text-xs font-semibold text-slate-800">Memory search & filters</h2></div>
        <button type="button" onClick={onReset} className="inline-flex items-center gap-1.5 text-[11px] font-medium text-blue-700 hover:text-blue-900">
          <RotateCcw size={13} />Clear filters
        </button>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        <FilterSelect id="filter-crisis-type" label="Crisis type" value={filters.crisisType} onChange={(value) => onFilter('crisisType', value as CrisisType | '')}>
          <option value="">All crisis types</option>
          {data.crisisTypes.map((type) => <option key={type} value={type}>{type}</option>)}
        </FilterSelect>
        <FilterSelect id="filter-supplier" label="Supplier" value={filters.supplier} onChange={(value) => onFilter('supplier', value)}>
          <option value="">All suppliers</option>
          {data.suppliers.map((supplier) => <option key={supplier} value={supplier}>{supplier}</option>)}
        </FilterSelect>
        <FilterSelect id="filter-outcome" label="Outcome" value={filters.outcome} onChange={(value) => onFilter('outcome', value as MemoryOutcome | '')}>
          <option value="">All outcomes</option>
          <option value="Successful">Successful · demo</option>
          <option value="Ineffective">Ineffective · demo</option>
        </FilterSelect>
        <DateFilter id="filter-date-from" label="From date" value={filters.dateFrom} max={filters.dateTo || undefined} onChange={(value) => onFilter('dateFrom', value)} />
        <DateFilter id="filter-date-to" label="To date" value={filters.dateTo} min={filters.dateFrom || undefined} onChange={(value) => onFilter('dateTo', value)} />
      </div>
    </section>
  )
}

function FilterSelect({
  id,
  label,
  value,
  onChange,
  children,
}: {
  id: string
  label: string
  value: string
  onChange: (value: string) => void
  children: ReactNode
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-[10px] font-semibold text-slate-500">{label}</label>
      <div className="relative">
        <select id={id} value={value} onChange={(event) => onChange(event.target.value)} className={`${inputClassName} appearance-none py-2.5 pr-8 text-xs`}>
          {children}
        </select>
        <ChevronDown size={14} className="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400" />
      </div>
    </div>
  )
}

function DateFilter({
  id,
  label,
  value,
  min,
  max,
  onChange,
}: {
  id: string
  label: string
  value: string
  min?: string
  max?: string
  onChange: (value: string) => void
}) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-[10px] font-semibold text-slate-500">{label}</label>
      <input id={id} type="date" value={value} min={min} max={max} onChange={(event) => onChange(event.target.value)} className={`${inputClassName} py-2 text-xs`} />
    </div>
  )
}
