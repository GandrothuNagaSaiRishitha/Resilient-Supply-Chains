import type { ApiResponse } from './api'
import type { CrisisType } from './crisisReport'

export type RiskSeverity = 'Low' | 'Medium' | 'High' | 'Critical'
export type ImpactDistributionCategory =
  | 'Inventory'
  | 'Orders'
  | 'Transportation'
  | 'Supplier'

export interface ImpactIncidentOption {
  id: string
  crisisType: CrisisType
  title: string
  reportedAt: string
}

export interface ImpactKpi {
  id: string
  label: string
  value: number
  unit?: string
  formattedValue: string
  severity: RiskSeverity
}

export interface AffectedProduct {
  id: string
  product: string
  component: string
  supplier: string
  shortage: number
  severity: RiskSeverity
}

export interface WarehouseImpact {
  id: string
  warehouse: string
  location: string
  availableInventory: number
  inventoryAtRisk: number
  coverageDays: number
  severity: RiskSeverity
}

export interface CustomerOrderRisk {
  id: string
  customer: string
  orderValue: number
  priority: RiskSeverity
  expectedDelayDays: number
}

export interface ImpactDistribution {
  category: ImpactDistributionCategory
  value: number
}

export interface SeverityIndicator {
  severity: RiskSeverity
  count: number
  description: string
}

export interface ImpactAssumptions {
  items: string[]
}

export interface ImpactAnalysis {
  incident: ImpactIncidentOption
  kpis: ImpactKpi[]
  affectedProducts: AffectedProduct[]
  warehouseImpacts: WarehouseImpact[]
  customerOrders: CustomerOrderRisk[]
  distribution: ImpactDistribution[]
  severityIndicators: SeverityIndicator[]
  assumptions: ImpactAssumptions
}

export type ImpactIncidentsResponse = ApiResponse<ImpactIncidentOption[]>
export type ImpactAnalysisResponse = ApiResponse<ImpactAnalysis>
