import type {
  BusinessUrgency,
  CrisisType,
} from './crisisReport'

export interface CrisisReportFormValues {
  crisisType: CrisisType | ''
  incidentTitle: string
  description: string
  supplierId: string
  shipmentId: string
  productComponent: string
  origin: string
  destination: string
  expectedDelayDays: string
  availableInventoryQuantity: string
  affectedOrders: string
  urgency: BusinessUrgency | ''
  incidentDate: string
}
