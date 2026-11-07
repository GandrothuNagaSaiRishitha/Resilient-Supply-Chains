import { useState, type FormEvent } from 'react'
import { AlertCircle, BookOpenCheck, CheckCircle2 } from 'lucide-react'
import type { DecisionReport, OutcomeFeedbackRequest } from '../../types/decision'
import type { DecisionOutcomeValues } from '../../types/decisionForm'
import type { RecoveryStrategyKey } from '../../types/simulation'
import { SectionHeader } from './DecisionUi'
import { inputClassName } from './decisionUtils'
import { isMockMode } from '../../services/apiConfig'

const initialOutcome: DecisionOutcomeValues = {
  strategyKey: '',
  actualAdditionalCost: '',
  actualDeliveryDelayDays: '',
  actualInventoryShortage: '',
  ordersAffected: '',
  successful: '',
  lessonsLearned: '',
  additionalNotes: '',
}

export default function OutcomeFeedbackForm({
  report,
  initialStrategyKey,
  onSubmit,
}: {
  report: DecisionReport
  initialStrategyKey: RecoveryStrategyKey
  onSubmit: (request: OutcomeFeedbackRequest) => Promise<string>
}) {
  const [values, setValues] = useState({ ...initialOutcome, strategyKey: initialStrategyKey })
  const [submitting, setSubmitting] = useState(false)
  const [submittedId, setSubmittedId] = useState<string | null>(null)
  const [error, setError] = useState(false)

  const setField = <K extends keyof DecisionOutcomeValues>(key: K, value: DecisionOutcomeValues[K]) => {
    setValues((current) => ({ ...current, [key]: value }))
    setSubmittedId(null)
    setError(false)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!values.strategyKey || !values.successful) return
    setSubmitting(true)
    setError(false)
    try {
      const request: OutcomeFeedbackRequest = {
        incidentId: report.scenario.incident.id,
        strategyKey: values.strategyKey,
        actualAdditionalCost: Number(values.actualAdditionalCost),
        actualDeliveryDelayDays: Number(values.actualDeliveryDelayDays),
        actualInventoryShortage: Number(values.actualInventoryShortage),
        ordersAffected: Number(values.ordersAffected),
        successful: values.successful === 'yes',
        lessonsLearned: values.lessonsLearned.trim(),
        additionalNotes: values.additionalNotes.trim(),
      }
      setSubmittedId(await onSubmit(request))
    } catch {
      setError(true)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/40">
      <SectionHeader icon={<BookOpenCheck size={18} />} title="Outcome feedback" description="Record what happened after execution to complete this decision record." tag={isMockMode ? 'Frontend demo only' : 'Backend API'} />
      <form className="p-5 sm:p-6" onSubmit={handleSubmit}>
        <p className="mb-4 rounded-xl border border-blue-100 bg-blue-50/60 p-3 text-[11px] leading-5 text-blue-800">
          {isMockMode ? 'Outcome values are entered by the user and held only in frontend demo memory. They are not sent to or persisted by a backend.' : 'Outcome feedback is submitted to the configured backend API. Persistence and processing depend on the backend implementation.'}
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="sm:col-span-2 lg:col-span-4">
            <label htmlFor="outcome-strategy" className="mb-1.5 block text-xs font-semibold text-slate-700">Selected strategy <span className="text-rose-500">*</span></label>
            <select id="outcome-strategy" className={inputClassName} value={values.strategyKey} onChange={(event) => setField('strategyKey', event.target.value as RecoveryStrategyKey)} required>
              {report.scenario.strategies.map((strategy) => <option key={strategy.key} value={strategy.key}>{strategy.name}</option>)}
            </select>
          </div>
          <NumberField id="actual-cost" label="Actual additional cost ($)" value={values.actualAdditionalCost} onChange={(value) => setField('actualAdditionalCost', value)} />
          <NumberField id="actual-delay" label="Actual delivery delay (days)" value={values.actualDeliveryDelayDays} onChange={(value) => setField('actualDeliveryDelayDays', value)} />
          <NumberField id="actual-shortage" label="Actual inventory shortage (units)" value={values.actualInventoryShortage} onChange={(value) => setField('actualInventoryShortage', value)} />
          <NumberField id="actual-orders" label="Orders affected" value={values.ordersAffected} onChange={(value) => setField('ordersAffected', value)} />
          <fieldset className="sm:col-span-2 lg:col-span-4">
            <legend className="mb-2 text-xs font-semibold text-slate-700">Was the strategy successful? <span className="text-rose-500">*</span></legend>
            <div className="flex flex-wrap gap-3">
              <SuccessOption label="Yes, successful" value="yes" selected={values.successful} onChange={(value) => setField('successful', value)} />
              <SuccessOption label="No, not successful" value="no" selected={values.successful} onChange={(value) => setField('successful', value)} />
            </div>
          </fieldset>
          <TextAreaField id="lessons-learned" label="Lessons learned" value={values.lessonsLearned} onChange={(value) => setField('lessonsLearned', value)} placeholder="What should the team remember for future incidents?" />
          <TextAreaField id="additional-notes" label="Additional notes" value={values.additionalNotes} onChange={(value) => setField('additionalNotes', value)} placeholder="Optional context about the actual outcome..." />
        </div>
        {submittedId && <div role="status" className="mt-4 flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800"><CheckCircle2 size={16} className="mt-0.5 shrink-0 text-emerald-600" />{isMockMode ? `Demo outcome recorded · ${submittedId}. It is held in frontend demo memory only.` : `Outcome recorded · ${submittedId}.`}</div>}
        {error && <div role="alert" className="mt-4 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800"><AlertCircle size={15} />{isMockMode ? 'Could not record the demo outcome. Please try again.' : 'Could not submit the outcome. Please try again.'}</div>}
        <div className="mt-4 flex justify-end">
          <button type="submit" disabled={submitting} className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60">
            <BookOpenCheck size={15} />{submitting ? (isMockMode ? 'Recording demo outcome...' : 'Submitting outcome...') : 'Submit Outcome'}
          </button>
        </div>
      </form>
    </section>
  )
}

function NumberField({ id, label, value, onChange }: { id: string; label: string; value: string; onChange: (value: string) => void }) {
  return (
    <div>
      <label htmlFor={id} className="mb-1.5 block text-xs font-semibold text-slate-700">{label} <span className="text-rose-500">*</span></label>
      <input id={id} type="number" min="0" step="1" className={inputClassName} value={value} onChange={(event) => onChange(event.target.value)} required />
    </div>
  )
}

function SuccessOption({
  label,
  value,
  selected,
  onChange,
}: {
  label: string
  value: 'yes' | 'no'
  selected: '' | 'yes' | 'no'
  onChange: (value: 'yes' | 'no') => void
}) {
  return (
    <label className={`inline-flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-xs transition ${selected === value ? 'border-blue-300 bg-blue-50 text-blue-800' : 'border-slate-200 text-slate-600 hover:bg-slate-50'}`}>
      <input type="radio" name="successful" value={value} checked={selected === value} onChange={() => onChange(value)} required className="accent-blue-600" />
      {label}
    </label>
  )
}

function TextAreaField({
  id,
  label,
  value,
  onChange,
  placeholder,
}: {
  id: string
  label: string
  value: string
  onChange: (value: string) => void
  placeholder: string
}) {
  return (
    <div className="sm:col-span-2">
      <label htmlFor={id} className="mb-1.5 block text-xs font-semibold text-slate-700">{label}</label>
      <textarea id={id} className={`${inputClassName} min-h-24 resize-y`} value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} rows={3} />
    </div>
  )
}
