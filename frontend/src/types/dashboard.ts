export type KpiIcon = 'disruptions' | 'shipments' | 'orders' | 'inventory'
export type KpiTone = 'blue' | 'amber' | 'violet' | 'rose'

export interface DashboardKpi {
  id: string
  label: string
  value: number
  unit?: string
  icon: KpiIcon
  tone: KpiTone
}

export interface DeliveryDelayTrendPoint {
  month: string
  avg_delay_days: number
  orders: number
}

export interface SupplierReliability {
  id: string
  name: string
  reliability_score: number
  on_time_rate: number
  avg_delay_days: number
  delivered_orders: number
  open_orders: number
  quality_complaints: number
}

export interface UpcomingDelivery {
  id: string
  order_number: string
  supplier: string
  promised_date: string
  priority: string
  status: string
}

export interface DashboardApiResponse {
  synthetic_demo_data: boolean
  generated_at: string
  kpis: {
    active_orders: number
    delivered_orders: number
    delayed_orders: number
    at_risk_orders: number
    avg_delivery_delay_days: number
    supplier_reliability_avg: number
    upcoming_deliveries_14d: number
    pending_alerts: number
    critical_bottlenecks: number
    suppliers: number
    total_orders: number
  }
  charts: {
    on_time_vs_delayed: Array<{ name: string; value: number }>
    supplier_reliability: SupplierReliability[]
    delay_trend: DeliveryDelayTrendPoint[]
    status_distribution: Array<{ status: string; count: number }>
    risk_distribution: Array<{ risk: string; count: number }>
  }
  upcoming_deliveries: UpcomingDelivery[]
}

export interface SupplierReliabilitySummary {
  score: number
  supplierCount: number
  generatedAt: string
}

export interface DashboardOverview {
  kpis: DashboardKpi[]
  supplierReliabilitySummary: SupplierReliabilitySummary
  deliveryDelayTrend: DeliveryDelayTrendPoint[]
  supplierReliability: SupplierReliability[]
  upcomingDeliveries: UpcomingDelivery[]
  pendingAlerts: number
}
