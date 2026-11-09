# SHOCKWAVE AI API Audit Report

Date: 2026-11-09

Scope: release worktree only. This audit did not modify PostgreSQL, Hindsight, application secrets, or the main worktree environment.

## Integration matrix

| Frontend section | API endpoint | Method | Request / response contract | Backend status | Verification |
|---|---|---:|---|---|---|
| Dashboard | `/api/v1/dashboard` | GET | No body; dashboard object at JSON root | Implemented in `backend/app/api/dashboard.py` | Static contract check; runtime blocked |
| Report a Crisis | `/api/crises/form-options` | GET | Organization suppliers/orders and crisis options in `data` | Implemented in `backend/app/api/crises.py` | Static contract check; runtime blocked |
| Report a Crisis | `/api/crises` | POST | Camel-case `CrisisReportCreate`; returns `data.incidentId` | Implemented and tenant-validating | Static contract check; runtime blocked |
| Impact Analysis | `/api/impacts/incidents` | GET | Organization incident list in `data` | Implemented in `backend/app/api/impacts.py` | Static contract check; runtime blocked |
| Impact Analysis | `/api/impacts/incidents/{incidentId}` | GET | UUID path; persisted orders/inventory/supplier analysis in `data` | Implemented and organization-scoped | Static contract check; runtime blocked |
| Recovery Simulator | `/api/recovery-simulations/incidents` | GET | Organization incident list in `data` | Implemented in `backend/app/api/recovery_simulations.py` | Static contract check; runtime blocked |
| Recovery Simulator | `/api/recovery-simulations/incidents/{incidentId}` | GET | UUID path; calculated strategies in `data` | Implemented and organization-scoped | Static contract check; runtime blocked |
| Recovery Simulator | `/api/recovery-simulations/confirmations` | POST | `incidentId`, `strategyKey`; persisted confirmation | Implemented and organization-scoped | Static contract check; runtime blocked |
| Decision Report | `/api/decisions/incidents` | GET | Organization incident list in `data` | Implemented in `backend/app/api/decisions.py` | Static contract check; runtime blocked |
| Decision Report | `/api/decisions/incidents/{incidentId}/recommendation` | GET | UUID path; scenario, Hindsight evidence, Groq recommendation/baseline status | Implemented; external services may degrade explicitly | Static contract check; runtime blocked |
| Decision Report | `/api/decisions/actions` | POST | `incidentId`, action, nullable strategy key, explanation | Implemented and persisted | Static contract check; runtime blocked |
| Decision Report | `/api/decisions/outcomes` | POST | Outcome metrics, lessons, notes; persists before Hindsight retention | Implemented; Hindsight unavailability is reported | Static contract check; runtime blocked |
| Memory Centre | `/api/memories/overview` | GET | Hindsight recall plus organization provenance in `data` | Implemented; 503 on unavailable Hindsight | Static contract check; runtime blocked |
| Memory Centre | `/api/memories` | GET | Optional crisis/supplier/outcome/date filters; recalled results in `data` | Implemented; 503 on unavailable Hindsight | Static contract check; runtime blocked |
| Memory Centre | `/api/memories/{memoryId}` | GET | Local provenance ID; recalled memory detail in `data` | Implemented and organization-scoped | Static contract check; runtime blocked |
| Decision Replay Lab | `/api/decision-replays/incidents` | GET | Organization incident list in `data` | Implemented in `backend/app/api/decision_replays.py` | Static contract check; runtime blocked |
| Decision Replay Lab | `/api/decision-replays/{incidentId}` | GET | Persisted decision/outcome plus current scenario and evidence | Implemented and organization-scoped | Static contract check; runtime blocked |
| Decision Replay Lab | `/api/decision-replays/{incidentId}/run` | POST | No body; analytical replay result in `data` | Implemented; original decision unchanged | Static contract check; runtime blocked |

Authentication is obtained by the frontend through `POST /api/v1/auth/demo-login`, then sent as a Bearer token. Protected backend routes derive organization context from token claims and verify user and organization ownership.

## Findings and changes

### Impact Analysis

- The backend incident list is a real organization-scoped query; it does not insert sample incidents.
- Inventory resolution now uses canonical, tenant- and supplier-scoped SKU/name matching. Similar SKUs, ambiguous names, and missing mappings are not treated as matches.
- The analysis no longer fabricates an affected-product row when no inventory mapping exists; it returns an explicit `inventoryMapping` status and omits unsupported inventory quantities.
- The previous empty state only explained that a crisis should be reported. It now includes a link to `/report-crisis` when the API returns an authentic empty list.
- The page previously discarded backend error details and showed only a generic failure. It now displays the normalized API error message and retains the retry action.
- No synthetic incident was added.

### Memory Centre

- Memory overview, search, and detail all use Hindsight-backed backend routes in API mode. They do not fall back to local records after an API failure.
- Hindsight unavailability is represented by HTTP 503 in the backend and an error state in the frontend, distinct from an empty successful result.
- The memory reset maintenance route requires owner/admin authorization, a demo organization, explicit confirmation, and a server-only `DEMO_MEMORY_RESET_TOKEN`; it is disabled when the token is unset. A failed remote bank deletion no longer deletes local provenance.
- Memory requests use `VITE_MEMORY_API_TIMEOUT_MS` (default 180 seconds). Decision recommendations use `VITE_DECISION_API_TIMEOUT_MS` (default 600 seconds), with bounded Hindsight reflect and Groq retries; demo login follows the general API timeout.

### Explicit data source and refresh behavior

- API mode is now the frontend default when `VITE_DATA_SOURCE` is unset. Synthetic mode remains available only through an explicit `VITE_DATA_SOURCE=mock` setting.
- Recovery Simulator, Decision Report, Decision Replay, and Impact Analysis now reconcile selected incident IDs when a refresh returns a changed or empty list. Dependent detail state is cleared instead of showing stale records or remaining in a loading state.

### Mock data

The `frontend/src/data/*MockData.ts` files are explicitly selected only when `VITE_DATA_SOURCE=mock`. API-mode services call the backend and reject normalized errors; they do not silently substitute mock records. The mock datasets remain available as a separately labeled development/demo mode.

### Release configuration and health safety

- Release backend settings now load the release project's root `.env`, matching the previously working project layout; no secret values were printed or changed.
- Health checks log dependency failures server-side and return availability status without exposing raw database or Hindsight exception text.
- PostgreSQL connection attempts and public Hindsight health checks are bounded to avoid a stalled readiness endpoint.
- Retained memories normalize provenance at the memory-service boundary: only `verified_business_fact` can be verified, non-verified sources are capped at confidence `0.8`, and caller metadata cannot overwrite reserved provenance fields.
- AI context treats absent provenance as unknown rather than verified; user-reported outcome provenance is retained through memory indexing and historical evidence.
- Decision outcome rows persist the `user_reported_fact` provenance (`verified: false`, confidence `0.8`) alongside the Hindsight memory metadata.
- Canonical SKU collisions are reported as ambiguous instead of being overwritten; recovery scenarios expose inventory mapping status and do not recommend a strategy when mapping is missing or ambiguous.
- Identical decision actions and outcome feedback retries return the existing persisted record ID instead of inserting a duplicate.
- Backend tests cover exact inventory matching, provenance, reset protection, and sanitized health failures.

## Verification status

Checks executed in the release worktree:

- All seven requested frontend sections and their service calls were inspected.
- `backend\.venv\Scripts\python.exe -c "import app.main"` passed.
- `backend\.venv\Scripts\python.exe -m pytest -q` passed: **35 passed**. Pytest and pytest-asyncio were missing from the venv and were installed there; no dependency manifest was changed.
- FastAPI started on port 8011 with startup seeding and the scheduler disabled. The backend root returned its JSON service descriptor.
- `/api/v1/health` returned a sanitized `degraded` response, and the same response was obtained through Vite's `/api` proxy.
- PostgreSQL at `127.0.0.1:5433` and Hindsight at `127.0.0.1:8888` were unreachable; health reported both unavailable. Groq was not configured. A live demo-login request returned HTTP 500 because PostgreSQL was unavailable.
- Frontend `npm run lint` and `npm run build` passed. The build has only the non-failing large-chunk advisory.
- Vite started on port 5179 and served the frontend. The Vite proxy reached FastAPI. `node_modules/.vite-temp` had Modify access; the previous EPERM was not reproduced, and no security settings were changed.
- Browser smoke checks opened all seven pages in API mode. They rendered loading/empty/error/retry states; no API failure switched to mock business data. The live database-backed workflow could not run.
- `git diff --check` passed after the implementation changes.

## Remaining blockers and requirement evidence

- Crisis creation, inventory reads, recovery confirmation, Groq recommendation generation, Hindsight retain/recall/reflect, decision replay, and outcome-to-memory integration were **not** end-to-end tested because PostgreSQL and Hindsight were unavailable and Groq was not configured.
- The project `master_prompt.md` calls for meaningful Band Desktop/agent coordination. Public Band documentation verifies that Band provides SDK-based agent and room coordination, but it is not an event-specific hackathon rubric. No official event requirements link or Band credentials were supplied; the Band requirement remains unverified and the app reports Band disabled.
- Port 8000 was already occupied by a process outside this task, so it was left untouched. The release API and Vite were tested on ports 8011 and 5179.
- The earlier `.vite-temp` EPERM's exact historical process/file-lock cause could not be established because it did not reproduce in this run.

No database migration, seed, database reset, Hindsight reset, or memory deletion was run. No end-to-end success is claimed.
