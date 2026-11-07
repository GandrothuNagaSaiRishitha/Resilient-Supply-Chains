import type { DashboardOverview } from '../types/dashboard'

export const dashboardMockData: DashboardOverview = {
  kpis: [
    { id: 'active-orders', label: 'Active Orders', value: 12, icon: 'orders', tone: 'blue' },
    { id: 'delayed-orders', label: 'Delayed Orders', value: 7, icon: 'shipments', tone: 'amber' },
    { id: 'at-risk-orders', label: 'At-risk Orders', value: 4, icon: 'disruptions', tone: 'rose' },
    { id: 'average-delivery-delay', label: 'Average Delivery Delay', value: 2.4, unit: 'days', icon: 'inventory', tone: 'violet' },
  ],
  supplierReliabilitySummary: {
    score: 82,
    supplierCount: 3,
    generatedAt: 'Just now · Demo data',
  },
  deliveryDelayTrend: [
    { month: '2026-01', avg_delay_days: 1.8, orders: 18 },
    { month: '2026-02', avg_delay_days: 2.4, orders: 21 },
    { month: '2026-03', avg_delay_days: 1.5, orders: 16 },
    { month: '2026-04', avg_delay_days: 2.1, orders: 23 },
  ],
  supplierReliability: [
    {
      id: 'supplier-1',
      name: 'Northstar Components',
      reliability_score: 91,
      on_time_rate: 0.94,
      avg_delay_days: 0.6,
      delivered_orders: 18,
      open_orders: 4,
      quality_complaints: 1,
    },
    {
      id: 'supplier-2',
      name: 'Pacific Freight',
      reliability_score: 82,
      on_time_rate: 0.85,
      avg_delay_days: 1.7,
      delivered_orders: 14,
      open_orders: 5,
      quality_complaints: 2,
    },
    {
      id: 'supplier-3',
      name: 'Alpine Materials',
      reliability_score: 73,
      on_time_rate: 0.76,
      avg_delay_days: 2.8,
      delivered_orders: 11,
      open_orders: 3,
      quality_complaints: 3,
    },
  ],
  upcomingDeliveries: [
    {
      id: 'order-1',
      order_number: 'PO-2481',
      supplier: 'Northstar Components',
      promised_date: '2026-11-10T00:00:00Z',
      priority: 'high',
      status: 'in_transit',
    },
    {
      id: 'order-2',
      order_number: 'PO-2479',
      supplier: 'Pacific Freight',
      promised_date: '2026-11-12T00:00:00Z',
      priority: 'normal',
      status: 'processing',
    },
  ],
  pendingAlerts: 2,
}
