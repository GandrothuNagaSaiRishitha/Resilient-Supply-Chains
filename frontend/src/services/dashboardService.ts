import { dashboardMockData } from '../data/dashboardMockData'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import api from './api'
import type { ApiResponse } from '../types/api'
import type { DashboardOverviewResponse } from '../types/dashboard'

export async function getDashboardOverview(): Promise<DashboardOverviewResponse> {
  if (isMockMode) return { data: dashboardMockData }
  const { data } = await api.get<ApiResponse<DashboardOverviewResponse['data']>>(apiEndpoints.dashboard)
  return data
}
