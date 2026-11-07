import { CalendarDays, ClipboardList } from 'lucide-react'
import FormField from '../FormField'
import FormSection from '../FormSection'
import { reportInputClass, urgencyColors } from './formStyles'
import type {
  BusinessUrgency,
  CrisisReportFormOptions,
  CrisisType,
} from '../../types/crisisReport'
import type { CrisisReportFormValues } from '../../types/crisisReportForm'

type Props = {
  values: CrisisReportFormValues
  options: CrisisReportFormOptions | null
  setField: <K extends keyof CrisisReportFormValues>(
    key: K,
    value: CrisisReportFormValues[K],
  ) => void
  changeCrisisType: (type: CrisisType | '') => void
}

export default function IncidentDetailsFields({
  values,
  options,
  setField,
  changeCrisisType,
}: Props) {
  return (
    <FormSection
      title="Incident details"
      description="Describe the event and set its urgency."
      icon={<ClipboardList size={18} />}
    >
      <FormField label="Crisis type" htmlFor="crisisType" required>
        <select
          id="crisisType"
          name="crisisType"
          className={reportInputClass}
          value={values.crisisType}
          onChange={(event) => changeCrisisType(event.target.value as CrisisType | '')}
          required
          disabled={!options}
        >
          <option value="">Select a crisis type</option>
          {options?.crisisTypes.map((crisisType) => (
            <option key={crisisType} value={crisisType}>{crisisType}</option>
          ))}
        </select>
      </FormField>
      <FormField label="Incident title" htmlFor="incidentTitle" required>
        <input
          id="incidentTitle"
          name="incidentTitle"
          className={reportInputClass}
          placeholder="e.g. Port closure delaying inbound components"
          value={values.incidentTitle}
          onChange={(event) => setField('incidentTitle', event.target.value)}
          maxLength={120}
          required
        />
      </FormField>
      <div className="sm:col-span-2">
        <FormField
          label="Detailed incident description"
          htmlFor="description"
          required
          hint="Include what happened, when it began, and any response already underway."
        >
          <textarea
            id="description"
            name="description"
            className={`${reportInputClass} min-h-28 resize-y`}
            placeholder="Provide the relevant context and known impact..."
            value={values.description}
            onChange={(event) => setField('description', event.target.value)}
            rows={4}
            maxLength={2000}
            required
          />
        </FormField>
      </div>
      <FormField
        label="Business urgency"
        htmlFor="urgency"
        required
        hint="Choose Critical only when immediate action is required."
      >
        <select
          id="urgency"
          name="urgency"
          className={`${reportInputClass} ${values.urgency ? urgencyColors[values.urgency] : ''}`}
          value={values.urgency}
          onChange={(event) => setField('urgency', event.target.value as BusinessUrgency | '')}
          required
          disabled={!options}
        >
          <option value="">Select urgency</option>
          {options?.urgencies.map((urgency) => <option key={urgency} value={urgency}>{urgency}</option>)}
        </select>
      </FormField>
      <FormField label="Incident date" htmlFor="incidentDate" required>
        <div className="relative">
          <CalendarDays size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            id="incidentDate"
            name="incidentDate"
            type="date"
            className={`${reportInputClass} pl-9`}
            value={values.incidentDate}
            onChange={(event) => setField('incidentDate', event.target.value)}
            required
          />
        </div>
      </FormField>
    </FormSection>
  )
}
