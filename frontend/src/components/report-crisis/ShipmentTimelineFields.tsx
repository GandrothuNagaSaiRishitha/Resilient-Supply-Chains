import { MapPin, Truck } from 'lucide-react'
import FormField from '../FormField'
import FormSection from '../FormSection'
import { reportInputClass } from './formStyles'
import type { CrisisReportFormOptions } from '../../types/crisisReport'
import type { CrisisReportFormValues } from '../../types/crisisReportForm'

type Props = {
  values: CrisisReportFormValues
  options: CrisisReportFormOptions | null
  setField: <K extends keyof CrisisReportFormValues>(
    key: K,
    value: CrisisReportFormValues[K],
  ) => void
}

export default function ShipmentTimelineFields({ values, options, setField }: Props) {
  const isShipment = values.crisisType === 'Shipment Disruption'
  const showDelay = isShipment || values.crisisType === 'Supplier Failure'
  if (!isShipment && !showDelay) return null
  const supplierOrders = options?.orders.filter((order) => order.supplierId === values.supplierId) ?? []

  return (
    <FormSection
      title="Shipment & timeline"
      description="Add movement details and estimated time impact."
      icon={<Truck size={18} />}
    >
      {isShipment && (
        <>
          <FormField label="Shipment ID" htmlFor="shipmentId" required>
            <select
              id="shipmentId"
              name="shipmentId"
              className={reportInputClass}
              value={values.shipmentId}
              onChange={(event) => {
                const order = supplierOrders.find((item) => item.orderNumber === event.target.value)
                setField('shipmentId', event.target.value)
                if (order) setField('productComponent', order.product)
              }}
              disabled={!values.supplierId || supplierOrders.length === 0}
              required
            >
              <option value="">{values.supplierId ? 'Select an open order' : 'Select a supplier first'}</option>
              {supplierOrders.map((order) => (
                <option key={order.id} value={order.orderNumber}>
                  {order.orderNumber} · {order.product} · {order.status.replaceAll('_', ' ')}
                </option>
              ))}
            </select>
            {values.supplierId && supplierOrders.length === 0 && (
              <p role="status" className="mt-1 text-[11px] leading-5 text-amber-700">
                No open orders are recorded for this supplier. Select a supplier with an active order or report a Supplier Failure/Inventory Shortage without linking a shipment.
              </p>
            )}
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
