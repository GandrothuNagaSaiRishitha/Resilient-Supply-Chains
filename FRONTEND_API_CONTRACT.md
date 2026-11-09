# Frontend API contract

This contract records the requests and response shapes actually used by the
frontend. It is not a proposal for additional backend endpoints. Paths below
are relative to `VITE_API_BASE_URL`; most API calls use the shared Axios client.
Successful responses must be JSON with the shape shown. Errors are normalized
from `{ message?, detail?, error?, code?, requestId?, details? }`.

## Integration-wide behavior

- `VITE_DATA_SOURCE` selects `mock` or `api`. The frontend defaults to `mock`
  when the variable is unset; `.env.example` shows API mode.
- In API mode, `VITE_API_BASE_URL` must be configured for production requests.
- The client sends `Accept: application/json`, has a 15-second timeout, and
  attaches a Bearer authorization header using the demo-login token.
- Before the first API call, the client obtains a token with
  `POST /api/v1/auth/demo-login`, no request body. Expected response:
  `{ "access_token": "..." }`. It stores the token in session storage.
- Except for the dashboard and demo-login responses, service methods expect
  response envelopes of `{ data: T, meta?: { requestId?, page?, pageSize?, total? } }`.
- Methods shown as `GET` have no request body. No pagination or status-code
  details beyond the frontend contracts are currently specified.
- The route registry is in `frontend/src/services/apiEndpoints.ts`; interfaces
  are in `frontend/src/types/` (replay interfaces are in
  `frontend/src/pages/DecisionReplay/types.ts`).

## Feature endpoint inventory

| Feature | Method and exact path | Request | Expected successful response |
|---|---|---|---|
| Dashboard | `GET /api/v1/dashboard` | None | Raw `DashboardApiResponse` (not wrapped in `{ data }`) |
| Crisis Reporter: form options | `GET /api/crises/form-options` | None | `ApiResponse<CrisisReportFormOptions>` |
| Crisis Reporter: submit | `POST /api/crises` | `CrisisReportRequest` | `ApiResponse<CrisisReportResponse>` |
| Impact Analysis: incidents | `GET /api/impacts/incidents` | None | `ApiResponse<ImpactIncidentOption[]>` |
| Impact Analysis: selected incident | `GET /api/impacts/incidents/{incidentId}` | None; URL-encoded `incidentId` | `ApiResponse<ImpactAnalysis>` |
| Recovery Strategies: incidents | `GET /api/recovery-simulations/incidents` | None | `ApiResponse<SimulationIncident[]>` |
| Recovery Strategies: scenario | `GET /api/recovery-simulations/incidents/{incidentId}` | None; URL-encoded `incidentId` | `ApiResponse<SimulationScenario>` |
| Recovery Strategies: confirm | `POST /api/recovery-simulations/confirmations` | `ConfirmStrategyRequest` | `ApiResponse<ConfirmStrategyResponse>` |
| Decision Report: incidents | `GET /api/decisions/incidents` | None | `ApiResponse<SimulationIncident[]>` |
| Decision Report: recommendation | `GET /api/decisions/incidents/{incidentId}/recommendation` | None; URL-encoded `incidentId` | `ApiResponse<DecisionReport>` |
| Decision Report: record action | `POST /api/decisions/actions` | `DecisionActionRequest` | `ApiResponse<DecisionActionResponse>` |
| Decision Report: outcome feedback | `POST /api/decisions/outcomes` | `OutcomeFeedbackRequest` | `ApiResponse<OutcomeFeedbackResponse>` |
| Decision Replay: incidents | `GET /api/decision-replays/incidents` | None | `ApiResponse<SimulationIncident[]>` |
| Decision Replay: record | `GET /api/decision-replays/{incidentId}` | None; URL-encoded `incidentId` | `ApiResponse<DecisionReplayRecord>` |
| Decision Replay: run | `POST /api/decision-replays/{incidentId}/run` | No body | `ApiResponse<{ incidentId, replayed, message }>` |
| Hindsight / Memory: overview | `GET /api/memories/overview` | None | `ApiResponse<MemoryCentreData>` |
| Hindsight / Memory: search | `GET /api/memories` | Query params listed below | `ApiResponse<HistoricalIncidentMemory[]>` |
| Hindsight / Memory: detail | `GET /api/memories/{memoryId}` | None; URL-encoded `memoryId` | `ApiResponse<HistoricalIncidentMemory>` |

### Request details

`CrisisReportRequest` fields are all sent (nullable values are explicit `null`):

- `crisisType`: `CrisisType`; `incidentTitle`, `description`, `supplierId`,
  `productComponent`: strings.
- `shipmentId`, `origin`, `destination`: string or `null`. They are populated
  for `Shipment Disruption`, otherwise `null`.
- `expectedDelayDays`: number or `null`; it is `null` for `Inventory Shortage`.
- `availableInventoryQuantity`: number or `null`; it is populated for
  `Inventory Shortage` and `Supplier Failure`.
- `affectedOrders`: number; `urgency`: `BusinessUrgency`; `incidentDate`: date
  string (`YYYY-MM-DD` from the form).
- UI validation requires crisis type, title, description, supplier,
  product/component, affected order count, urgency, and incident date. Shipment
  ID and origin/destination are required for shipment disruption. Expected
  delay is required for shipment disruption and supplier failure. Inventory
  quantity is required for inventory shortage.

`ConfirmStrategyRequest`: `{ incidentId: string, strategyKey: RecoveryStrategyKey }`.

`DecisionActionRequest`: `{ incidentId: string, action: 'accepted' | 'rejected' | 'alternative', strategyKey: RecoveryStrategyKey | null, explanation: string }`.
The UI sends an empty explanation when none was entered. Rejecting sends a
`null` strategy key.

`OutcomeFeedbackRequest`: `{ incidentId: string, strategyKey: RecoveryStrategyKey, actualAdditionalCost: number, actualDeliveryDelayDays: number, actualInventoryShortage: number, ordersAffected: number, successful: boolean, lessonsLearned: string, additionalNotes: string }`.
The four numeric fields and success choice are required in the UI;
`lessonsLearned` and `additionalNotes` may be empty strings.

Memory search sends any non-empty subset of query parameters:
`crisisType`, `supplier`, `outcome`, `dateFrom`, `dateTo`. `crisisType` is a
`CrisisType`; `outcome` is `Successful | Ineffective`; the date parameters are
date strings. It does not currently request pagination.

## TypeScript response and request shapes

These are API-facing frontend types. Type aliases below retain the JSON
envelopes expected by the service methods.

```ts
export type CrisisType =
  | 'Shipment Disruption'
  | 'Supplier Failure'
  | 'Inventory Shortage'
export type BusinessUrgency = 'Low' | 'Medium' | 'High' | 'Critical'

export interface ApiResponseMeta {
  requestId?: string
  page?: number
  pageSize?: number
  total?: number
}
export interface ApiResponse<T> {
  data: T
  meta?: ApiResponseMeta
}
export interface ApiErrorPayload {
  message?: string
  detail?: string
  error?: string
  code?: string
  requestId?: string
  details?: unknown
}

export interface CrisisReportFormOptions {
  crisisTypes: CrisisType[]
  suppliers: Array<{ id: string; name: string }>
  urgencies: BusinessUrgency[]
}
export interface CrisisReportRequest {
  crisisType: CrisisType
  incidentTitle: string
  description: string
  supplierId: string
  shipmentId: string | null
  productComponent: string
  origin: string | null
  destination: string | null
  expectedDelayDays: number | null
  availableInventoryQuantity: number | null
  affectedOrders: number
  urgency: BusinessUrgency
  incidentDate: string
}
export interface CrisisReportResponse {
  incidentId: string
  demo?: boolean
  message: string
}
export type CrisisFormOptionsResponse = ApiResponse<CrisisReportFormOptions>
export type CrisisReportSubmitResponse = ApiResponse<CrisisReportResponse>

export type RiskSeverity = 'Low' | 'Medium' | 'High' | 'Critical'
export type ImpactDistributionCategory =
  | 'Inventory' | 'Orders' | 'Transportation' | 'Supplier'
export interface ImpactIncidentOption {
  id: string
  crisisType: CrisisType
  title: string
  reportedAt: string
}
export interface ImpactKpi {
  id: string
  label: string
  value: number
  unit?: string
  formattedValue: string
  severity: RiskSeverity
}
export interface AffectedProduct {
  id: string
  product: string
  component: string
  supplier: string
  shortage: number
  severity: RiskSeverity
}
export interface WarehouseImpact {
  id: string
  warehouse: string
  location: string
  availableInventory: number
  inventoryAtRisk: number
  coverageDays: number
  severity: RiskSeverity
}
export interface CustomerOrderRisk {
  id: string
  customer: string
  orderValue: number
  priority: RiskSeverity
  expectedDelayDays: number
}
export interface ImpactDistribution {
  category: ImpactDistributionCategory
  value: number
}
export interface SeverityIndicator {
  severity: RiskSeverity
  count: number
  description: string
}
export interface ImpactAnalysis {
  incident: ImpactIncidentOption
  kpis: ImpactKpi[]
  affectedProducts: AffectedProduct[]
  warehouseImpacts: WarehouseImpact[]
  customerOrders: CustomerOrderRisk[]
  distribution: ImpactDistribution[]
  severityIndicators: SeverityIndicator[]
  assumptions: { items: string[] }
}
export type ImpactIncidentsResponse = ApiResponse<ImpactIncidentOption[]>
export type ImpactAnalysisResponse = ApiResponse<ImpactAnalysis>

export type RecoveryStrategyKey =
  | 'wait' | 'reroute' | 'emergency-sourcing' | 'redistribute'
export type FeasibilityStatus = 'Feasible' | 'Conditional' | 'Not feasible'
export interface SimulationIncident {
  id: string
  crisisType: CrisisType
  title: string
  reportedAt: string
}
export interface IncidentConstraint {
  id: string
  label: string
  detail: string
}
export interface RecoveryStrategy {
  key: RecoveryStrategyKey
  name: string
  summary: string
  additionalCost: number
  deliveryDelayDays: number
  projectedShortageUnits: number
  riskLevel: RiskSeverity
  feasibility: FeasibilityStatus
  feasibilityNote: string
  tradeOff: string
}
export interface SimulationScenario {
  incident: SimulationIncident
  summary: string
  constraints: IncidentConstraint[]
  strategies: RecoveryStrategy[]
  recommendedStrategyKey: RecoveryStrategyKey
  recommendationExplanation: string
}
export interface ConfirmStrategyRequest {
  incidentId: string
  strategyKey: RecoveryStrategyKey
}
export interface ConfirmStrategyResponse {
  confirmationId: string
  incidentId: string
  strategyKey: RecoveryStrategyKey
  demo?: boolean
  message: string
}

export type DecisionAction = 'accepted' | 'rejected' | 'alternative'
export interface DecisionIncidentContext {
  description: string
  urgency: BusinessUrgency
  currentImpact: string
}
export interface HistoricalEvidence {
  id: string
  incidentDate: string
  crisisType: string
  previousStrategy: string
  outcome: string
  lessonLearned: string
  demoRecord?: boolean
}
export interface AlternativeStrategyContext {
  strategyKey: RecoveryStrategyKey
  whyLessSuitable: string
}
export interface MemoryComparison {
  memoryFreeStrategyKey: RecoveryStrategyKey
  memoryFreeExplanation: string
  memoryInformedStrategyKey: RecoveryStrategyKey
  memoryInformedExplanation: string
  evidenceIds: string[]
  whatChanged: string
}
export interface DecisionReport {
  scenario: SimulationScenario
  incidentContext: DecisionIncidentContext
  expectedBenefits: string[]
  risksAndTradeoffs: string[]
  executionConditions: string[]
  alternatives: AlternativeStrategyContext[]
  historicalEvidence: HistoricalEvidence[]
  memoryComparison: MemoryComparison
  demoDataNotice?: string
}
export interface DecisionActionRequest {
  incidentId: string
  action: DecisionAction
  strategyKey: RecoveryStrategyKey | null
  explanation: string
}
export interface DecisionActionResponse {
  confirmationId: string
  demo?: boolean
  message: string
}
export interface OutcomeFeedbackRequest {
  incidentId: string
  strategyKey: RecoveryStrategyKey
  actualAdditionalCost: number
  actualDeliveryDelayDays: number
  actualInventoryShortage: number
  ordersAffected: number
  successful: boolean
  lessonsLearned: string
  additionalNotes: string
}
export interface OutcomeFeedbackResponse {
  outcomeId: string
  demo?: boolean
  message: string
}
export type DecisionIncidentsResponse = ApiResponse<SimulationIncident[]>
export type DecisionReportResponse = ApiResponse<DecisionReport>
export type DecisionActionApiResponse = ApiResponse<DecisionActionResponse>
export type OutcomeFeedbackApiResponse = ApiResponse<OutcomeFeedbackResponse>

export interface ReplayHistoricalEvidence {
  id: string
  incidentDate: string
  crisisType: string
  decision: string
  actualOutcome: string
  lesson: string
}
export interface ReplayActualOutcome {
  additionalCost: number
  deliveryDelayDays: number
  inventoryShortageUnits: number
  ordersAffected: number
  successful: boolean
  summary: string
}
export interface DecisionReplayRecord {
  incident: SimulationIncident
  scenario: SimulationScenario
  originalStrategyKey: RecoveryStrategyKey
  actualOutcome: ReplayActualOutcome
  memoryFreeStrategyKey: RecoveryStrategyKey
  memoryInformedStrategyKey: RecoveryStrategyKey
  historicalEvidence: ReplayHistoricalEvidence[]
  evidenceExplanation: string
  comparisonExplanation: string
}
export type DecisionReplayListResponse = ApiResponse<SimulationIncident[]>
export type DecisionReplayResponse = ApiResponse<DecisionReplayRecord>
export type ReplayActionResponse = ApiResponse<{
  incidentId: string
  replayed: boolean
  message: string
}>

export type MemoryOutcome = 'Successful' | 'Ineffective'
export interface HistoricalIncidentMemory {
  id: string
  incidentDate: string
  crisisType: CrisisType
  supplier: string
  title: string
  description: string
  decisionTaken: string
  expectedResult: string
  actualOutcome: string
  outcome: MemoryOutcome
  lessonLearned: string
  demoRecord?: boolean
}
export interface MemoryOverviewStats {
  totalHistoricalIncidents: number
  successfulStrategies: number
  ineffectiveStrategies: number
  lessonsRetained: number
  demo?: boolean
}
export interface LearnedInsight {
  id: string
  category:
    | 'Recurring pattern'
    | 'Successful strategy'
    | 'Ineffective approach'
    | 'Lesson learned'
  title: string
  description: string
  evidenceCount: number
}
export interface MemoryLifecycleStage {
  id: 'retain' | 'recall' | 'reflect'
  title: string
  description: string
  example: string
}
export interface MemoryCentreData {
  stats: MemoryOverviewStats
  memories: HistoricalIncidentMemory[]
  insights: LearnedInsight[]
  lifecycle: MemoryLifecycleStage[]
  crisisTypes: CrisisType[]
  suppliers: string[]
}
export interface MemoryFilters {
  crisisType: CrisisType | ''
  supplier: string
  outcome: MemoryOutcome | ''
  dateFrom: string
  dateTo: string
}
export type MemoryCentreResponse = ApiResponse<MemoryCentreData>
export type MemorySearchResponse = ApiResponse<HistoricalIncidentMemory[]>
export type MemoryDetailResponse = ApiResponse<HistoricalIncidentMemory>

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
```

## Mock usage and page states

| Feature | Mock data used? | Loading / error / empty coverage |
|---|---|---|
| Dashboard | Yes, in mock mode (`dashboardMockData`). | Loading skeleton and retryable error. No dedicated empty state; child widgets receive empty arrays if returned. |
| Crisis Reporter | Yes: form options from `crisisReportMockData`; submission returns a demo confirmation and does not create an incident. | Options loading, error with retry, and zero-supplier notice; submit loading, error alert, and success confirmation. No separate empty page state. |
| Impact Analysis | Yes (`impactMockData`). | Loading skeleton, retryable error, and no-incidents/no-analysis empty state. |
| Recovery Strategies | Yes (`simulationMockData`). | Loading skeleton, retryable error, empty incident state, confirmation progress/error/result. |
| Decision Report | Yes (`decisionMockData` plus `simulationMockData`). | Loading skeleton, retryable error, empty report state, action progress/error/confirmation, and outcome-feedback progress/error/success. |
| Decision Replay | Yes (`decisionReplayMockData` and `simulationMockData`). | Loading skeleton, retryable error, no-incident empty message, and replay progress/result message. |
| Hindsight / Memory | Yes (`memoryMockData`); search and detail operate on local demo records. | Overview loading and retryable error, search progress/error and no-results messages, detail loading/error dialog. |
| AI Agent | No implemented UI, page route, service, endpoint, or TypeScript contract was found. | Not implemented. No backend endpoint can be stated from frontend evidence. |

## Integration gaps and handoff notes

- **AI Agent:** absent from `App.tsx`, pages, services, and endpoint registry.
  No API requirements can be derived without a product/backend decision.
- **Hindsight:** memory centre, decision report evidence, and replay data have
  frontend surfaces, but no direct Hindsight SDK/service integration exists.
  The only explicit memory endpoints are the three `/api/memories...` calls
  above; the frontend labels mock mode as having no Hindsight connection.
- **Recovery and Decision incident lists:** both expect the same
  `SimulationIncident` shape from separate list endpoints. They do not call the
  impact incidents endpoint.
- **Dashboard response envelope:** unlike all other domain data calls, the
  dashboard service expects the response fields at the JSON root, not under
  `data`.
- **Authentication path:** demo-login is defined as `/api/v1/auth/demo-login`;
  dashboard is `/api/v1/dashboard`, while all other feature routes are rooted
  at `/api/...`. Preserve these exact paths unless frontend and backend owners
  agree on a coordinated change.
- No extra endpoints for Dashboard alerts, AI execution, Hindsight retrieval,
  or crisis-created incident propagation are present in the frontend.

## Frontend validation

Run from `frontend/`:

- `npm run build` — passed (`tsc -b` and Vite production build). Vite emitted a
  non-failing advisory that the main minified JavaScript chunk is over 500 kB.
- `npm run lint` — passed.
