import type { ApiResponse } from './api'

export type KpiIcon = 'disruptions' | 'shipments' | 'orders' | 'inventory'
export type KpiTone = 'blue' | 'amber' | 'violet' | 'rose'
export type IncidentSeverity = 'Critical' | 'High' | 'Medium' | 'Low'
export type IncidentStatus = 'Investigating' | 'Mitigating' | 'Monitoring' | 'Resolved'
export type RecoveryActivityStatus = 'In progress' | 'Completed'

export interface DashboardKpi {
  id: string
  label: string
  value: number
  unit?: string
  icon: KpiIcon
  tone: KpiTone
}

export interface DisruptionTrendPoint {
  date: string
  disruptions: number
  delayedShipments: number
}

export interface SupplyChainHealth {
  status: string
  score: number
  summary: string
  updatedAt: string
}

export interface DashboardIncident {
  id: string
  disruptionType: string
  location: string
  severity: IncidentSeverity
  status: IncidentStatus
  date: string
}

export interface RecoveryActivity {
  id: string
  title: string
  description: string
  owner: string
  time: string
  status: RecoveryActivityStatus
}

export interface PriorityAlert {
  id: string
  title: string
  description: string
  severity: IncidentSeverity
  location: string
  occurredAt: string
}

export interface DashboardOverview {
  kpis: DashboardKpi[]
  health: SupplyChainHealth
  disruptionTrend: DisruptionTrendPoint[]
  incidents: DashboardIncident[]
  recoveryActivities: RecoveryActivity[]
  alerts: PriorityAlert[]
}

export type DashboardOverviewResponse = ApiResponse<DashboardOverview>
