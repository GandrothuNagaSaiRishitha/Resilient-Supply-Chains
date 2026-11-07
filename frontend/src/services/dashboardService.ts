import { dashboardMockData } from '../data/dashboardMockData'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import api from './api'
import type { DashboardApiResponse, DashboardOverview } from '../types/dashboard'

function mapDashboardResponse(response: DashboardApiResponse): DashboardOverview {
  return {
    kpis: [
      {
        id: 'active-orders',
        label: 'Active Orders',
        value: response.kpis.active_orders,
        icon: 'orders',
        tone: 'blue',
      },
      {
        id: 'delayed-orders',
        label: 'Delayed Orders',
        value: response.kpis.delayed_orders,
        icon: 'shipments',
        tone: 'amber',
      },
      {
        id: 'at-risk-orders',
        label: 'At-risk Orders',
        value: response.kpis.at_risk_orders,
        icon: 'disruptions',
        tone: 'rose',
      },
      {
        id: 'average-delivery-delay',
        label: 'Average Delivery Delay',
        value: response.kpis.avg_delivery_delay_days,
        unit: 'days',
        icon: 'inventory',
        tone: 'violet',
      },
    ],
    supplierReliabilitySummary: {
      score: response.kpis.supplier_reliability_avg,
      supplierCount: response.kpis.suppliers,
      generatedAt: response.generated_at,
    },
    deliveryDelayTrend: response.charts.delay_trend,
    supplierReliability: response.charts.supplier_reliability,
    upcomingDeliveries: response.upcoming_deliveries,
    pendingAlerts: response.kpis.pending_alerts,
  }
}

export async function getDashboardOverview(): Promise<DashboardOverview> {
  if (isMockMode) return dashboardMockData
  const { data } = await api.get<DashboardApiResponse>(apiEndpoints.dashboard)
  return mapDashboardResponse(data)
}
