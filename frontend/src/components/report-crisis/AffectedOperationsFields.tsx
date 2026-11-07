import { Package } from 'lucide-react'
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

export default function AffectedOperationsFields({
  values,
  options,
  setField,
}: Props) {
  const showInventory = values.crisisType === 'Inventory Shortage' || values.crisisType === 'Supplier Failure'
  const requiredInventory = values.crisisType === 'Inventory Shortage'

  return (
    <FormSection
      title="Affected operations"
      description="Identify the supplier and product/component involved."
      icon={<Package size={18} />}
    >
      <FormField label="Supplier" htmlFor="supplierId" required>
        <select
          id="supplierId"
          name="supplierId"
          className={reportInputClass}
          value={values.supplierId}
          onChange={(event) => setField('supplierId', event.target.value)}
          required
          disabled={!options}
        >
          <option value="">Select a supplier</option>
          {options?.suppliers.map((supplier) => (
            <option key={supplier.id} value={supplier.id}>{supplier.name}</option>
          ))}
        </select>
      </FormField>
      <FormField label="Product / component affected" htmlFor="productComponent" required>
        <input
          id="productComponent"
          name="productComponent"
          className={reportInputClass}
          placeholder="e.g. Control module CM-204"
          value={values.productComponent}
          onChange={(event) => setField('productComponent', event.target.value)}
          required
        />
      </FormField>
      {showInventory && (
        <FormField
          label="Available inventory quantity"
          htmlFor="availableInventoryQuantity"
          required={requiredInventory}
          hint="Current on-hand quantity for the affected component."
        >
          <input
            id="availableInventoryQuantity"
            name="availableInventoryQuantity"
            type="number"
            min="0"
            step="1"
            className={reportInputClass}
            placeholder="e.g. 240"
            value={values.availableInventoryQuantity}
            onChange={(event) => setField('availableInventoryQuantity', event.target.value)}
            required={requiredInventory}
          />
        </FormField>
      )}
      <FormField
        label="Number of affected orders"
        htmlFor="affectedOrders"
        required
        hint="Enter 0 if no orders are currently impacted."
      >
        <input
          id="affectedOrders"
          name="affectedOrders"
          type="number"
          min="0"
          step="1"
          className={reportInputClass}
          placeholder="e.g. 18"
          value={values.affectedOrders}
          onChange={(event) => setField('affectedOrders', event.target.value)}
          required
        />
      </FormField>
    </FormSection>
  )
}
