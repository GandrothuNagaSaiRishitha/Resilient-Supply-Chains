import { decisionReplayMockData } from '../data/decisionReplayMockData'
import { simulationIncidents, simulationScenarios } from '../data/simulationMockData'
import api from './api'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import type { ApiResponse } from '../types/api'
import type {
  DecisionReplayListResponse,
  DecisionReplayResponse,
  ReplayActionResponse,
} from '../pages/DecisionReplay/types'

export async function getDecisionReplayIncidents(): Promise<DecisionReplayListResponse> {
  if (isMockMode) return { data: simulationIncidents }
  const { data } = await api.get<ApiResponse<DecisionReplayListResponse['data']>>(apiEndpoints.replayIncidents)
  return data
}

export async function getDecisionReplay(incidentId: string): Promise<DecisionReplayResponse> {
  if (!isMockMode) {
    const { data } = await api.get<ApiResponse<DecisionReplayResponse['data']>>(apiEndpoints.decisionReplay(incidentId))
    return data
  }
  const incident = simulationIncidents.find((item) => item.id === incidentId)
  const scenario = simulationScenarios[incidentId]
  const mock = decisionReplayMockData[incidentId]

  if (!incident || !scenario || !mock) {
    throw new Error(`No illustrative decision replay is available for incident ${incidentId}.`)
  }

  return {
    data: {
      ...mock,
      incident,
      scenario,
    },
  }
}

export async function replayIncident(incidentId: string): Promise<ReplayActionResponse> {
  if (!isMockMode) {
    const { data } = await api.post<ApiResponse<ReplayActionResponse['data']>>(apiEndpoints.replayAction(incidentId))
    return data
  }
  await getDecisionReplay(incidentId)
  return {
    data: {
      incidentId,
      replayed: true,
      message: 'Illustrative replay refreshed from static demo records. No AI or Hindsight request was made.',
    },
  }
}
