import { useEffect, useState, type FormEvent } from 'react'
import {
  getCrisisReportFormOptions,
  submitCrisisReport,
} from '../services/crisisReportService'
import type {
  CrisisReportFormOptions,
  CrisisReportRequest,
  CrisisReportResponse,
  CrisisType,
} from '../types/crisisReport'
import type { CrisisReportFormValues } from '../types/crisisReportForm'

function getLocalDate(): string {
  const now = new Date()
  return new Date(now.getTime() - now.getTimezoneOffset() * 60_000)
    .toISOString()
    .slice(0, 10)
}

const initialFormValues: CrisisReportFormValues = {
  crisisType: '',
  incidentTitle: '',
  description: '',
  supplierId: '',
  shipmentId: '',
  productComponent: '',
  origin: '',
  destination: '',
  expectedDelayDays: '',
  availableInventoryQuantity: '',
  affectedOrders: '',
  urgency: '',
  incidentDate: getLocalDate(),
}

function toOptionalNumber(value: string): number | null {
  return value === '' ? null : Number(value)
}

function toRequest(values: CrisisReportFormValues): CrisisReportRequest {
  if (!values.crisisType || !values.urgency) {
    throw new Error('Required crisis type or urgency was missing.')
  }
  const shipmentDisruption = values.crisisType === 'Shipment Disruption'
  const inventoryShortage = values.crisisType === 'Inventory Shortage'

  return {
    crisisType: values.crisisType,
    incidentTitle: values.incidentTitle.trim(),
    description: values.description.trim(),
    supplierId: values.supplierId,
    shipmentId: shipmentDisruption ? values.shipmentId.trim() : null,
    productComponent: values.productComponent.trim(),
    origin: shipmentDisruption ? values.origin.trim() : null,
    destination: shipmentDisruption ? values.destination.trim() : null,
    expectedDelayDays: inventoryShortage ? null : toOptionalNumber(values.expectedDelayDays),
    availableInventoryQuantity:
      inventoryShortage || values.crisisType === 'Supplier Failure'
        ? toOptionalNumber(values.availableInventoryQuantity)
        : null,
    affectedOrders: Number(values.affectedOrders),
    urgency: values.urgency,
    incidentDate: values.incidentDate,
  }
}

export function useCrisisReportForm() {
  const [values, setValues] = useState(initialFormValues)
  const [options, setOptions] = useState<CrisisReportFormOptions | null>(null)
  const [optionsLoading, setOptionsLoading] = useState(true)
  const [optionsError, setOptionsError] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(false)
  const [confirmation, setConfirmation] = useState<CrisisReportResponse | null>(null)
  const [optionsRetryKey, setOptionsRetryKey] = useState(0)

  useEffect(() => {
    let active = true
    getCrisisReportFormOptions()
      .then(({ data }) => { if (active) setOptions(data) })
      .catch(() => { if (active) setOptionsError(true) })
      .finally(() => { if (active) setOptionsLoading(false) })
    return () => { active = false }
  }, [optionsRetryKey])

  const setField = <K extends keyof CrisisReportFormValues>(
    key: K,
    value: CrisisReportFormValues[K],
  ) => {
    setValues((current) => ({ ...current, [key]: value }))
    setConfirmation(null)
    setSubmitError(false)
  }

  const changeCrisisType = (crisisType: CrisisType | '') => {
    setValues((current) => ({
      ...current,
      crisisType,
      shipmentId: crisisType === 'Shipment Disruption' ? current.shipmentId : '',
      origin: crisisType === 'Shipment Disruption' ? current.origin : '',
      destination: crisisType === 'Shipment Disruption' ? current.destination : '',
      expectedDelayDays:
        crisisType === 'Shipment Disruption' || crisisType === 'Supplier Failure'
          ? current.expectedDelayDays
          : '',
      availableInventoryQuantity:
        crisisType === 'Inventory Shortage' || crisisType === 'Supplier Failure'
          ? current.availableInventoryQuantity
          : '',
    }))
    setConfirmation(null)
    setSubmitError(false)
  }

  const reset = () => {
    setValues({ ...initialFormValues, incidentDate: getLocalDate() })
    setConfirmation(null)
    setSubmitError(false)
  }

  const retryOptions = () => {
    setOptions(null)
    setOptionsLoading(true)
    setOptionsError(false)
    setOptionsRetryKey((key) => key + 1)
  }

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setSubmitError(false)
    setConfirmation(null)
    try {
      const { data } = await submitCrisisReport(toRequest(values))
      setConfirmation(data)
    } catch {
      setSubmitError(true)
    } finally {
      setSubmitting(false)
    }
  }

  return {
    values,
    options,
    optionsLoading,
    optionsError,
    submitting,
    submitError,
    confirmation,
    setField,
    changeCrisisType,
    reset,
    retryOptions,
    submit,
  }
}
