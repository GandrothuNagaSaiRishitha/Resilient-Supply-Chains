import { decisionMockData } from '../data/decisionMockData'
import { simulationIncidents, simulationScenarios } from '../data/simulationMockData'
import api from './api'
import { apiEndpoints } from './apiEndpoints'
import { isMockMode } from './apiConfig'
import type { ApiResponse } from '../types/api'
import type {
  DecisionActionApiResponse,
  DecisionActionRequest,
  DecisionIncidentsResponse,
  DecisionReport,
  DecisionReportResponse,
  OutcomeFeedbackApiResponse,
  OutcomeFeedbackRequest,
} from '../types/decision'

const demoOutcomeRecords: OutcomeFeedbackRequest[] = []

export async function getDecisionIncidents(): Promise<DecisionIncidentsResponse> {
  if (isMockMode) return { data: simulationIncidents }
  const { data } = await api.get<ApiResponse<DecisionIncidentsResponse['data']>>(apiEndpoints.decisionIncidents)
  return data
}

export async function getDecisionReport(
  incidentId: string,
): Promise<DecisionReportResponse> {
  if (!isMockMode) {
    const { data } = await api.get<ApiResponse<DecisionReportResponse['data']>>(apiEndpoints.decisionReport(incidentId))
    return data
  }
  const scenario = simulationScenarios[incidentId]
  const decisionContext = decisionMockData[incidentId]

  if (!scenario || !decisionContext) {
    throw new Error(`No demo decision report is available for incident ${incidentId}.`)
  }

  const report: DecisionReport = { ...decisionContext, scenario }
  return { data: report }
}

export async function submitDecisionAction(
  request: DecisionActionRequest,
): Promise<DecisionActionApiResponse> {
  if (!isMockMode) {
    const { data } = await api.post<ApiResponse<DecisionActionApiResponse['data']>>(apiEndpoints.decisionActions, request)
    return data
  }

  return {
    data: {
      confirmationId: `DECISION-DEMO-${Date.now().toString(36).toUpperCase()}`,
      demo: true,
      message: 'Demo confirmation only. No decision was saved to a backend.',
    },
  }
}

export async function submitOutcomeFeedback(
  request: OutcomeFeedbackRequest,
): Promise<OutcomeFeedbackApiResponse> {
  if (!isMockMode) {
    const { data } = await api.post<ApiResponse<OutcomeFeedbackApiResponse['data']>>(apiEndpoints.outcomeFeedback, request)
    return data
  }
  demoOutcomeRecords.push(request)

  return {
    data: {
      outcomeId: `OUTCOME-DEMO-${Date.now().toString(36).toUpperCase()}`,
      demo: true,
      message: 'Outcome stored in frontend demo memory only; it is not persisted to a backend.',
    },
  }
}
