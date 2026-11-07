# SHOCKWAVE AI Frontend Integration

## Architecture

- `src/pages/` contains route-level screens; reusable page sections live in `src/components/`.
- `src/types/` contains domain models and shared API envelope/error types.
- `src/data/*MockData.ts` contains the current illustrative datasets.
- `src/services/` owns data access. Each service selects mock or API behavior using `VITE_DATA_SOURCE`.
- `src/hooks/` contains stateful page workflows; Decision Replay has a feature-local hook and types under `src/pages/DecisionReplay/`.
- `src/App.tsx` defines routes. `Layout` provides the shared sidebar, navbar, and responsive content shell.
- `src/services/api.ts` is the shared Axios client. It uses `VITE_API_BASE_URL`, a 15-second timeout, JSON accept headers, and normalizes Axios/backend errors to `ApiClientError`.

The shared response envelope is `ApiResponse<T>`:

```json
{
  "data": {},
  "meta": {
    "requestId": "optional",
    "page": 1,
    "pageSize": 25,
    "total": 100
  }
}
```

`meta` is optional and its fields are optional. Services expect the backend response to use this envelope and intentionally do not substitute mock results when an API request fails.

The client normalizes common error bodies (`message`, `detail`, or `error`) and optionally captures `code`, `requestId`, and `details`. Backend error contract:

```json
{
  "message": "Human-readable error",
  "code": "OPTIONAL_STABLE_CODE",
  "requestId": "optional",
  "details": {}
}
```

## Environment

Copy `.env.example` to `.env.local` and set:

| Variable | Required | Meaning |
|---|---:|---|
| `VITE_DATA_SOURCE` | No | `mock` (default) or `api`. Any other value is rejected during app configuration. |
| `VITE_API_BASE_URL` | In API mode | Backend origin/base path, for example `http://127.0.0.1:8000`. Never put credentials or API keys here. |

The Axios request timeout is currently fixed at 15 seconds. The API mode requires a non-empty base URL and will return a normalized configuration error if missing.

## Service functions and backend contract

The Dashboard route and response below match the FastAPI backend. Other paths remain frontend proposals and must be confirmed before use. Paths are centralized in `src/services/apiEndpoints.ts`.

| Feature | Service functions | Method and path | Expected response data |
|---|---|---|---|
| Dashboard | `getDashboardOverview()` | `GET /api/v1/dashboard` (Bearer token from `POST /api/v1/auth/demo-login`) | Direct dashboard payload: `kpis`, `charts`, `upcoming_deliveries`, `generated_at`, `synthetic_demo_data` |
| Crisis reporting | `getCrisisReportFormOptions()` | `GET /api/crises/form-options` | `CrisisReportFormOptions` (`crisisTypes`, `suppliers`, `urgencies`) |
| Crisis reporting | `submitCrisisReport(request)` | `POST /api/crises` | `CrisisReportResponse` (`incidentId`, optional `demo`, `message`) |
| Impact analysis | `getImpactIncidents()` | `GET /api/impacts/incidents` | `ImpactIncidentOption[]` |
| Impact analysis | `getImpactAnalysis(incidentId)` | `GET /api/impacts/incidents/{incidentId}` | `ImpactAnalysis` |
| Recovery simulation | `getSimulationIncidents()` | `GET /api/recovery-simulations/incidents` | `SimulationIncident[]` |
| Recovery simulation | `getSimulationScenario(incidentId)` | `GET /api/recovery-simulations/incidents/{incidentId}` | `SimulationScenario` |
| Recovery simulation | `confirmRecoveryStrategy(request)` | `POST /api/recovery-simulations/confirmations` | `ConfirmStrategyResponse` |
| Decision recommendations | `getDecisionIncidents()` | `GET /api/decisions/incidents` | `SimulationIncident[]` |
| Decision recommendations | `getDecisionReport(incidentId)` | `GET /api/decisions/incidents/{incidentId}/recommendation` | `DecisionReport` |
| Decision actions | `submitDecisionAction(request)` | `POST /api/decisions/actions` | `DecisionActionResponse` |
| Outcome feedback | `submitOutcomeFeedback(request)` | `POST /api/decisions/outcomes` | `OutcomeFeedbackResponse` |
| Memory retrieval | `getMemoryCentreData()` | `GET /api/memories/overview` | `MemoryCentreData` |
| Memory retrieval | `searchMemories(filters)` | `GET /api/memories` with filter query parameters | `HistoricalIncidentMemory[]` |
| Memory retrieval | `getMemoryDetail(memoryId)` | `GET /api/memories/{memoryId}` | `HistoricalIncidentMemory` |
| Decision replay | `getDecisionReplayIncidents()` | `GET /api/decision-replays/incidents` | `SimulationIncident[]` |
| Decision replay | `getDecisionReplay(incidentId)` | `GET /api/decision-replays/{incidentId}` | `DecisionReplayRecord` |
| Decision replay | `replayIncident(incidentId)` | `POST /api/decision-replays/{incidentId}/run` | replay confirmation/message data |

### Request bodies

The domain request interfaces in `src/types/` are the source of truth for request field names and types:

- `CrisisReportRequest`: crisis type, title, description, supplier ID, optional shipment/product route details, optional delay and inventory values, affected-order count, urgency, and incident date.
- `ConfirmStrategyRequest`: `incidentId`, `strategyKey`.
- `DecisionActionRequest`: `incidentId`, action (`accepted`, `rejected`, or `alternative`), nullable strategy key, and explanation.
- `OutcomeFeedbackRequest`: incident and selected strategy, actual cost/delay/shortage/order values, success boolean, lessons, and notes.
- Memory search sends the non-empty `MemoryFilters` fields (`crisisType`, `supplier`, `outcome`, `dateFrom`, `dateTo`) as query parameters.
- Decision replay currently requires only the selected incident ID in the proposed replay path. Agree any replay controls/options with the backend before extending this contract.

The feature types currently describe the response `data` structures. Some domain fields originated as mock-only records and may need to be versioned or made optional once real backend schemas are agreed. The optional `demo` markers must not be used by the backend as a substitute for an explicit source/provenance contract.

## Source selection and failure behavior

- `mock` mode serves only the local data files and preserves the existing demo experience.
- `api` mode calls Axios and returns only the backend response. Network errors, HTTP errors, malformed configuration, and missing records reject through the shared normalized error path; services do not silently fall back to mock data.
- Page hooks already expose loading/error states for dashboard, impact, recovery, memory, decision report, and decision replay. Crisis report options now have loading, empty supplier, and retry states. Empty table/list/chart states are present where data can be absent.
- The Memory Centre browser does not call Hindsight. A backend may connect Hindsight behind the proposed memory endpoints; that is a backend implementation/contract decision and must be documented as such.
- The navbar indicates whether the configured source is mock or API. In API mode, record provenance and real persistence still depend on the backend response and must not be inferred by the frontend.

## Integration steps

1. Agree and document endpoint paths, request/response schemas, auth, CORS, error format, and pagination with the backend team. The Dashboard path/schema are confirmed; other paths are provisional.
2. Update `apiEndpoints.ts` and the response/request domain types to match the confirmed OpenAPI/backend contract.
3. Configure the local/deployment environment with `VITE_DATA_SOURCE=api` and `VITE_API_BASE_URL`; inject secrets only through an approved server-side/auth mechanism, never source code or a Vite-exposed variable.
4. Verify each service with contract/integration tests, including non-2xx errors, timeouts, empty results, and invalid IDs. Do not mask failures with mock values.
5. Confirm CORS/auth policy and backend Hindsight provenance before enabling memory endpoints for production.
6. Build with `npm run build`, run `npm run lint`, and smoke-test all routes against the agreed backend.

## Features still using mock data by default

When `VITE_DATA_SOURCE` is unset or `mock`, **all seven pages** use the existing illustrative mock datasets. In API mode the Dashboard calls the confirmed backend endpoint and does not fall back to mock data if the request fails. Other pages still call their proposed endpoints.
