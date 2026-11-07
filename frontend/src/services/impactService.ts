import {
  impactAnalysisByIncident,
  impactIncidents,
} from '../data/impactMockData'
import api from './api'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import type { ApiResponse } from '../types/api'
import type {
  ImpactAnalysisResponse,
  ImpactIncidentsResponse,
} from '../types/impact'

export async function getImpactIncidents(): Promise<ImpactIncidentsResponse> {
  if (isMockMode) return { data: impactIncidents }
  const { data } = await api.get<ApiResponse<ImpactIncidentsResponse['data']>>(apiEndpoints.impactIncidents)
  return data
}

export async function getImpactAnalysis(
  incidentId: string,
): Promise<ImpactAnalysisResponse> {
  if (!isMockMode) {
    const { data } = await api.get<ApiResponse<ImpactAnalysisResponse['data']>>(apiEndpoints.impactAnalysis(incidentId))
    return data
  }
  const analysis = impactAnalysisByIncident[incidentId]
  if (!analysis) {
    throw new Error(`No demo impact analysis is available for incident ${incidentId}.`)
  }

  return { data: analysis }
}
