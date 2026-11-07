import { crisisReportFormOptions } from '../data/crisisReportMockData'
import api from './api'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import type {
  CrisisReportFormOptions,
  CrisisReportRequest,
  CrisisReportResponse,
} from '../types/crisisReport'
import type { ApiResponse } from '../types/api'

export async function getCrisisReportFormOptions(): Promise<ApiResponse<CrisisReportFormOptions>> {
  if (isMockMode) return { data: crisisReportFormOptions }
  const { data } = await api.get<ApiResponse<CrisisReportFormOptions>>(apiEndpoints.crisisFormOptions)
  return data
}

export async function submitCrisisReport(
  report: CrisisReportRequest,
): Promise<ApiResponse<CrisisReportResponse>> {
  if (!isMockMode) {
    const { data } = await api.post<ApiResponse<CrisisReportResponse>>(apiEndpoints.crises, report)
    return data
  }
  return {
    data: {
      incidentId: `INC-DEMO-${Date.now().toString(36).toUpperCase()}`,
      demo: true,
      message: 'Demo confirmation only. No backend incident was created.',
    },
  }
}
