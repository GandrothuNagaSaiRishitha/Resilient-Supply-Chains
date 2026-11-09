import { AlertCircle, CheckCircle2, RotateCcw, Send } from 'lucide-react'
import { Link } from 'react-router-dom'
import AffectedOperationsFields from '../components/report-crisis/AffectedOperationsFields'
import IncidentDetailsFields from '../components/report-crisis/IncidentDetailsFields'
import ShipmentTimelineFields from '../components/report-crisis/ShipmentTimelineFields'
import { useCrisisReportForm } from '../hooks/useCrisisReportForm'
import { isMockMode } from '../services/apiConfig'

export default function ReportCrisisPage() {
  const form = useCrisisReportForm()

  return (
    <section className="mx-auto max-w-[1080px]">
      <div className="mb-6">
        <p className="mb-2 text-sm text-slate-500">Workspace / Report a Crisis</p>
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900 sm:text-[28px]">Report a Crisis</h1>
            <p className="mt-1.5 text-sm text-slate-500">Share disruption details to help your team assess and coordinate a response.</p>
          </div>
          <span className="inline-flex w-fit items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-[11px] font-semibold tracking-wide text-blue-700">
            <span className="size-1.5 rounded-full bg-blue-500" />{isMockMode ? 'DEMO REPORTING · NO BACKEND' : 'API REPORTING'}
          </span>
        </div>
      </div>

      {form.confirmation && (
        <div className="mb-5 flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4" role="status" aria-live="polite">
          <CheckCircle2 className="mt-0.5 shrink-0 text-emerald-600" size={19} />
          <div>
            <p className="text-sm font-semibold text-emerald-900">{form.confirmation.demo ? 'Demo report prepared' : 'Incident report submitted'} · {form.confirmation.incidentId}</p>
            <p className="mt-1 text-xs leading-5 text-emerald-800">{form.confirmation.message}</p>
            {!form.confirmation.demo && <Link to={`/decision-report?incidentId=${encodeURIComponent(form.confirmation.incidentId)}`} className="mt-3 inline-flex items-center gap-2 rounded-lg bg-emerald-700 px-3 py-2 text-xs font-semibold text-white transition hover:bg-emerald-800">Open memory-informed decision report</Link>}
          </div>
        </div>
      )}
      {form.submitError && (
        <div className="mb-5 flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800" role="alert">
          <AlertCircle size={17} />{form.submitError}
        </div>
      )}
      {form.optionsError && (
        <div className="mb-5 flex items-center justify-between gap-3 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800" role="alert">
          <span className="inline-flex items-center gap-2"><AlertCircle size={17} />{form.optionsError}</span>
          <button type="button" onClick={form.retryOptions} className="shrink-0 font-semibold underline underline-offset-2">Retry</button>
        </div>
      )}
      {form.optionsLoading && <p role="status" className="mb-5 rounded-xl border border-slate-200 bg-white p-3 text-xs text-slate-500">Loading crisis form options…</p>}
      {form.options && form.options.suppliers.length === 0 && (
        <p role="status" className="mb-5 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">No suppliers are available from the current data source. Submission is unavailable until supplier options are provided.</p>
      )}

      <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_280px]">
        <form className="space-y-5" onSubmit={form.submit}>
          <IncidentDetailsFields
            values={form.values}
            options={form.options}
            setField={form.setField}
            changeCrisisType={form.changeCrisisType}
          />
          <AffectedOperationsFields
            values={form.values}
            options={form.options}
            setField={form.setField}
          />
          <ShipmentTimelineFields values={form.values} options={form.options} setField={form.setField} />
          <div className="flex flex-col-reverse gap-3 border-t border-slate-200 pt-5 sm:flex-row sm:justify-end">
            <button type="button" onClick={form.reset} className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900">
              <RotateCcw size={15} />Reset
            </button>
            <button type="submit" disabled={form.submitting || !form.options || form.options.suppliers.length === 0} className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm shadow-blue-600/20 transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
              <Send size={15} />{form.submitting ? (isMockMode ? 'Preparing demo report...' : 'Submitting report...') : 'Submit Crisis'}
            </button>
          </div>
        </form>

        <aside className="rounded-2xl border border-blue-100 bg-blue-50/70 p-5 xl:sticky xl:top-6">
          <div className="mb-3 flex size-9 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm shadow-blue-900/5">
            <AlertCircle size={18} />
          </div>
          <h2 className="text-sm font-semibold text-slate-900">What happens next?</h2>
          <p className="mt-2 text-xs leading-5 text-slate-600">
            A complete report gives your response team the context to assess impact and coordinate next steps.
          </p>
          <ul className="mt-4 space-y-3 text-xs leading-5 text-slate-600">
            <li className="flex gap-2"><StepNumber number="1" />Review the incident details for accuracy.</li>
            <li className="flex gap-2"><StepNumber number="2" />Share relevant supplier, shipment, and impact information.</li>
            <li className="flex gap-2"><StepNumber number="3" />Coordinate response actions with your team.</li>
          </ul>
          <div className="mt-5 rounded-xl border border-blue-100 bg-white/80 p-3">
            <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-blue-700">{isMockMode ? 'Demo environment' : 'Connected workflow'}</p>
            <p className="mt-1 text-[11px] leading-5 text-slate-500">{isMockMode ? 'Submission generates a demo reference only. No backend incident is created or sent.' : 'Submitting creates an organization-scoped incident record that powers impact and recovery workflows.'}</p>
          </div>
        </aside>
      </div>
    </section>
  )
}

function StepNumber({ number }: { number: string }) {
  return (
    <span className="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded-full bg-blue-100 text-[10px] font-semibold text-blue-700">
      {number}
    </span>
  )
}
