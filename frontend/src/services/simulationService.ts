import {
  simulationIncidents,
  simulationScenarios,
} from '../data/simulationMockData'
import api from './api'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import type { ApiResponse } from '../types/api'
import type {
  ConfirmStrategyApiResponse,
  ConfirmStrategyRequest,
  SimulationIncidentsResponse,
  SimulationScenarioResponse,
} from '../types/simulation'

export async function getSimulationIncidents(): Promise<SimulationIncidentsResponse> {
  if (isMockMode) return { data: simulationIncidents }
  const { data } = await api.get<ApiResponse<SimulationIncidentsResponse['data']>>(apiEndpoints.simulationIncidents)
  return data
}

export async function getSimulationScenario(
  incidentId: string,
): Promise<SimulationScenarioResponse> {
  if (!isMockMode) {
    const { data } = await api.get<ApiResponse<SimulationScenarioResponse['data']>>(apiEndpoints.simulationScenario(incidentId))
    return data
  }
  const scenario = simulationScenarios[incidentId]
  if (!scenario) {
    throw new Error(`No demo simulation is available for incident ${incidentId}.`)
  }

  return { data: scenario }
}

export async function confirmRecoveryStrategy(
  request: ConfirmStrategyRequest,
): Promise<ConfirmStrategyApiResponse> {
  if (!isMockMode) {
    const { data } = await api.post<ApiResponse<ConfirmStrategyApiResponse['data']>>(apiEndpoints.simulationConfirm, request)
    return data
  }
  return {
    data: {
      confirmationId: `SIM-DEMO-${Date.now().toString(36).toUpperCase()}`,
      incidentId: request.incidentId,
      strategyKey: request.strategyKey,
      demo: true,
      message: 'Demo confirmation only. No strategy decision was saved to a backend.',
    },
  }
}
