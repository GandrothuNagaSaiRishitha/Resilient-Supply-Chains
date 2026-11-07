export type CrisisType =
  | 'Shipment Disruption'
  | 'Supplier Failure'
  | 'Inventory Shortage'

export type BusinessUrgency = 'Low' | 'Medium' | 'High' | 'Critical'

export interface CrisisReportFormOptions {
  crisisTypes: CrisisType[]
  suppliers: Array<{ id: string; name: string }>
  urgencies: BusinessUrgency[]
}

export interface CrisisReportRequest {
  crisisType: CrisisType
  incidentTitle: string
  description: string
  supplierId: string
  shipmentId: string | null
  productComponent: string
  origin: string | null
  destination: string | null
  expectedDelayDays: number | null
  availableInventoryQuantity: number | null
  affectedOrders: number
  urgency: BusinessUrgency
  incidentDate: string
}

export interface CrisisReportResponse {
  incidentId: string
  demo?: boolean
  message: string
}
