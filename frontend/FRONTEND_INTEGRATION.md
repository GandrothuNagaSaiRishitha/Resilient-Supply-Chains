# SHOCKWAVE AI Frontend Integration

## Architecture

- `src/pages/` contains route-level screens; reusable page sections live in `src/components/`.
- `src/types/` contains domain models and shared API envelope/error types.
- `src/data/*MockData.ts` contains the current illustrative datasets.
- `src/services/` owns data access. Each service selects mock or API behavior using `VITE_DATA_SOURCE`.
- `src/hooks/` contains stateful page workflows; Decision Replay has a feature-local hook and types under `src/pages/DecisionReplay/`.
- `src/App.tsx` defines routes. `Layout` provides the shared sidebar, navbar, and responsive content shell.
- `src/services/api.ts` is the shared Axios client. It uses `VITE_API_BASE_URL`, a configurable general timeout (`VITE_API_TIMEOUT_MS`, default 15 seconds), JSON accept headers, and normalizes Axios/backend errors to `ApiClientError`. Memory requests use `VITE_MEMORY_API_TIMEOUT_MS` (default 180 seconds), and decision recommendations use `VITE_DECISION_API_TIMEOUT_MS` (default 600 seconds), because those workflows can wait on Hindsight and Groq.

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
| `VITE_DATA_SOURCE` | No | `api` (default) or explicitly opted-in `mock`. Any other value is rejected during app configuration. |
| `VITE_API_BASE_URL` | In API mode | Backend origin/base path, for example `http://127.0.0.1:8000`. Never put credentials or API keys here. |
| `VITE_API_TIMEOUT_MS` | No | General API and demo-login request timeout in milliseconds; default `15000`. |
| `VITE_MEMORY_API_TIMEOUT_MS` | No | Hindsight-backed memory endpoint timeout in milliseconds; default `180000`. |
| `VITE_DECISION_API_TIMEOUT_MS` | No | Decision recommendation timeout in milliseconds; default `600000`. |

The general Axios request timeout defaults to 15 seconds and can be configured with `VITE_API_TIMEOUT_MS`. Memory requests use the separately configurable `VITE_MEMORY_API_TIMEOUT_MS` and default to 180 seconds; decision recommendation requests use `VITE_DECISION_API_TIMEOUT_MS` and default to 600 seconds. The API mode requires a non-empty base URL and will return a normalized configuration error if missing.

## Service functions and backend contract

The feature paths below match the registered FastAPI routes. Paths are centralized in `src/services/apiEndpoints.ts`; the backend's generated OpenAPI schema at `/openapi.json` is authoritative.

| Feature | Service functions | Method and path | Expected response data |
|---|---|---|---|
| Dashboard | `getDashboardOverview()` | `GET /api/v1/dashboard` (Bearer token from `POST /api/v1/auth/demo-login`) | Direct dashboard payload: `kpis`, `charts`, `upcoming_deliveries`, `generated_at`, `synthetic_demo_data` |
| Crisis reporting | `getCrisisReportFormOptions()` | `GET /api/crises/form-options` | `CrisisReportFormOptions` (`crisisTypes`, tenant-scoped `suppliers` and open `orders`, `urgencies`) |
| Crisis reporting | `submitCrisisReport(request)` | `POST /api/crises` | `CrisisReportResponse` (`incidentId`, optional `demo`, `message`) |
| Impact analysis | `getImpactIncidents()` | `GET /api/impacts/incidents` | `ImpactIncidentOption[]` |
| Impact analysis | `getImpactAnalysis(incidentId)` | `GET /api/impacts/incidents/{incidentId}` | `ImpactAnalysis` |
| Recovery simulation | `getSimulationIncidents()` | `GET /api/recovery-simulations/incidents` | `SimulationIncident[]` |
| Recovery simulation | `getSimulationScenario(incidentId)` | `GET /api/recovery-simulations/incidents/{incidentId}` | `SimulationScenario` |
| Recovery simulation | `confirmRecoveryStrategy(request)` | `POST /api/recovery-simulations/confirmations` | `ConfirmStrategyResponse` |
| Decision recommendations | `getDecisionIncidents()` | `GET /api/decisions/incidents` | `SimulationIncident[]` |
| Decision recommendations | `getDecisionReport(incidentId)` | `GET /api/decisions/incidents/{incidentId}/recommendation` | `DecisionReport`, including `aiRecommendation`, `memoryStatus`, and `reflectionStatus` |
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
- Decision replay currently requires only the selected incident ID. The Decision Report accepts `?incidentId=...` to open a newly submitted incident directly.

The feature types currently describe the response `data` structures. Some domain fields originated as mock-only records and may need to be versioned or made optional once real backend schemas are agreed. The optional `demo` markers must not be used by the backend as a substitute for an explicit source/provenance contract.

## Source selection and failure behavior

- `mock` mode serves only the local data files and preserves the existing demo experience.
- `api` mode calls Axios and returns only the backend response. Network errors, HTTP errors, malformed configuration, and missing records reject through the shared normalized error path; services do not silently fall back to mock data.
- Page hooks already expose loading/error states for dashboard, impact, recovery, memory, decision report, and decision replay. Crisis report options now have loading, empty supplier, and retry states. Empty table/list/chart states are present where data can be absent.
- The browser calls the configured memory API; the backend uses the official Hindsight client for organization-scoped retain, recall, and reflect. The browser never connects directly to Hindsight.
- Decision replay distinguishes Hindsight `available`, `empty`, and `unavailable` statuses. Without a recalled comparable strategy, the UI shows the baseline only and does not claim successful recall.
- The navbar indicates whether the configured source is mock or API. In API mode, record provenance and real persistence still depend on the backend response and must not be inferred by the frontend.
- Recovery scenarios expose `inventoryMapping`; `missing` or `ambiguous` mappings are reported by the backend instead of being silently represented as zero inventory.
- Identical decision and outcome retries are deduplicated by the backend and return the already-persisted record ID.

## Integration steps

1. Keep this contract and `apiEndpoints.ts` aligned with FastAPI's generated OpenAPI schema when routes change.
2. Keep response/request domain types aligned with the actual endpoint envelopes and backend tests.
3. Configure the local/deployment environment with `VITE_DATA_SOURCE=api` and `VITE_API_BASE_URL`; inject secrets only through an approved server-side/auth mechanism, never source code or a Vite-exposed variable.
4. Verify each service with contract/integration tests, including non-2xx errors, timeouts, empty results, and invalid IDs. Do not mask failures with mock values.
5. Confirm CORS/auth policy and backend Hindsight provenance before enabling memory endpoints for production.
6. Build with `npm run build`, run `npm run lint`, and smoke-test all routes against the agreed backend.

## Features still using mock data by default

When `VITE_DATA_SOURCE` is explicitly `mock`, pages use their illustrative local datasets. When it is unset or `api`, feature services call the backend endpoints above and reject normalized errors rather than silently falling back to mock responses.
