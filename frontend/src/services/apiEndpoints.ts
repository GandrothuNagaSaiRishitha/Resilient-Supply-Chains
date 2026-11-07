/**
 * Proposed frontend/backend paths only. Confirm all routes with the backend
 * contract before deployment; see FRONTEND_INTEGRATION.md.
 */
export const apiEndpoints = {
  dashboard: '/api/dashboard/overview',
  crisisFormOptions: '/api/crises/form-options',
  crises: '/api/crises',
  impactIncidents: '/api/impacts/incidents',
  impactAnalysis: (incidentId: string) => `/api/impacts/incidents/${encodeURIComponent(incidentId)}`,
  simulationIncidents: '/api/recovery-simulations/incidents',
  simulationScenario: (incidentId: string) => `/api/recovery-simulations/incidents/${encodeURIComponent(incidentId)}`,
  simulationConfirm: '/api/recovery-simulations/confirmations',
  decisionIncidents: '/api/decisions/incidents',
  decisionReport: (incidentId: string) => `/api/decisions/incidents/${encodeURIComponent(incidentId)}/recommendation`,
  decisionActions: '/api/decisions/actions',
  outcomeFeedback: '/api/decisions/outcomes',
  memoryOverview: '/api/memories/overview',
  memorySearch: '/api/memories',
  memoryDetail: (memoryId: string) => `/api/memories/${encodeURIComponent(memoryId)}`,
  replayIncidents: '/api/decision-replays/incidents',
  decisionReplay: (incidentId: string) => `/api/decision-replays/${encodeURIComponent(incidentId)}`,
  replayAction: (incidentId: string) => `/api/decision-replays/${encodeURIComponent(incidentId)}/run`,
} as const
