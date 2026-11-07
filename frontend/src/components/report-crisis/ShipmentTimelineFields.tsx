import { MapPin, Truck } from 'lucide-react'
import FormField from '../FormField'
import FormSection from '../FormSection'
import { reportInputClass } from './formStyles'
import type { CrisisReportFormValues } from '../../types/crisisReportForm'

type Props = {
  values: CrisisReportFormValues
  setField: <K extends keyof CrisisReportFormValues>(
    key: K,
    value: CrisisReportFormValues[K],
  ) => void
}

export default function ShipmentTimelineFields({ values, setField }: Props) {
  const isShipment = values.crisisType === 'Shipment Disruption'
  const showDelay = isShipment || values.crisisType === 'Supplier Failure'
  if (!isShipment && !showDelay) return null

  return (
    <FormSection
      title="Shipment & timeline"
      description="Add movement details and estimated time impact."
      icon={<Truck size={18} />}
    >
      {isShipment && (
        <>
          <FormField label="Shipment ID" htmlFor="shipmentId" required>
            <input
              id="shipmentId"
              name="shipmentId"
              className={reportInputClass}
              placeholder="Enter a purchase order number"
              value={values.shipmentId}
              onChange={(event) => setField('shipmentId', event.target.value)}
              required
            />
          </FormField>
          <LocationField
            id="origin"
            label="Origin"
            placeholder="City, port or facility"
            value={values.origin}
            onChange={(value) => setField('origin', value)}
          />
          <LocationField
            id="destination"
            label="Destination"
            placeholder="City, port or facility"
            value={values.destination}
            onChange={(value) => setField('destination', value)}
          />
        </>
      )}
      {showDelay && (
        <FormField
          label="Expected delay"
          htmlFor="expectedDelayDays"
          required
          hint="Estimated impact in calendar days."
        >
          <div className="relative">
            <input
              id="expectedDelayDays"
              name="expectedDelayDays"
              type="number"
              min="0"
              step="1"
              className={`${reportInputClass} pr-14`}
              placeholder="e.g. 5"
              value={values.expectedDelayDays}
              onChange={(event) => setField('expectedDelayDays', event.target.value)}
              required
            />
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400">
              days
            </span>
          </div>
        </FormField>
      )}
    </FormSection>
  )
}

function LocationField({
  id,
  label,
  placeholder,
  value,
  onChange,
}: {
  id: string
  label: string
  placeholder: string
  value: string
  onChange: (value: string) => void
}) {
  return (
    <FormField label={label} htmlFor={id} required>
      <div className="relative">
        <MapPin size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          id={id}
          name={id}
          className={`${reportInputClass} pl-9`}
          placeholder={placeholder}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          required
        />
      </div>
    </FormField>
  )
}
