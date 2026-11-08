# SHOCKWAVE AI – Next Steps Implementation Guide

## 1. Project Overview

SHOCKWAVE AI is an adaptive supply-chain crisis intelligence system. It helps organizations understand supply-chain disruptions, assess their impact, simulate recovery strategies, and make evidence-based decisions.

### Current Technology Stack
- Frontend: React, TypeScript, Vite
- Backend: FastAPI
- Database: PostgreSQL
- AI decision generation: Groq
- Organizational memory: Hindsight

### Core Workflow
1. Report a supply-chain crisis.
2. Analyse the operational impact.
3. Simulate possible recovery strategies.
4. Generate an AI decision report using historical evidence.
5. Record the selected decision.
6. Record the actual outcome.
7. Retain outcome information in organizational memory.
8. Retrieve historical evidence when a similar crisis occurs again.

## 2. Important Instructions

- Preserve the existing working architecture and API contracts.
- Do not replace working functionality with mock or hardcoded data.
- Do not delete existing database records, historical decisions, or memory data.
- Maintain organization-level data isolation.
- Keep mock/demo functionality separate from API mode.
- Do not expose API keys, database credentials, or environment secrets.
- Add tests for every important backend change.

## 3. Correct Product and Inventory Matching

**Priority: High**

### Problem
Inventory matching must not rely on loose substring comparisons. Similar SKUs or product names can produce incorrect inventory and impact calculations.

### Required work
- Review `backend/app/api/common.py`.
- Review its usage in:
  - `backend/app/api/impacts.py`
  - `backend/app/api/recovery_simulations.py`
- Use canonical SKU or product identifiers for matching.
- Support extracting an SKU embedded in a product description, followed by an exact canonical match.
- Handle missing and ambiguous product mappings explicitly.
- Never silently treat missing inventory as zero.
- Preserve organization and supplier filtering.

### Tests
- Exact SKU match.
- SKU embedded in a component description.
- Similar SKUs such as `ABC123` and `ABC1234`.
- Duplicate product names.
- Wrong supplier.
- Wrong organization.
- Missing product mapping.
- Ambiguous product mapping.

## 4. Correct Outcome Provenance

**Priority: High**

### Problem
User-submitted outcome feedback must not automatically be represented as independently verified business information.

### Required work
- Review:
  - `backend/app/api/decisions.py`
  - `backend/app/api/memories.py`
  - `backend/app/services/memory.py`
  - `backend/app/services/agent.py`
- Preserve provenance when an outcome moves through the API, memory service, and AI context.
- Use `user_reported_fact` for information submitted by a user but not independently verified.
- Reserve verified provenance for independently verified information.
- Ensure confidence values reflect the evidence available.

### Tests
- User-reported outcomes retain their provenance.
- Verified outcomes retain their verified status.
- Groq context distinguishes reported and verified information.
- Historical memory records remain intact.

## 5. AI Recommendation Performance and Timeout Handling

**Priority: High**

### Problem
AI recommendation generation may take longer than the frontend request timeout.

### Required work
- Review `frontend/src/hooks/useDecisionReport.ts`.
- Review `frontend/src/services/decisionService.ts`.
- Review `backend/app/api/decisions.py`.
- Review `backend/app/services/agent.py` and `backend/app/services/memory.py`.
- Align frontend and backend timeout behaviour.
- Avoid unnecessary repeated Groq and Hindsight calls.
- Consider caching, persisted reports, or an asynchronous job flow where appropriate.
- Provide useful loading and error states.
- Ensure users do not accidentally create duplicate decisions when retrying.

## 6. Demo Memory Reset and Data Protection

**Priority: High**

### Required work
- Review the demo authentication and memory reset routes.
- Review `backend/app/api/memories.py`.
- Protect destructive reset operations from unauthorized access.
- Prevent a public demo user from deleting shared organizational memory.
- Ensure database seeding does not overwrite populated data.
- Preserve existing historical records.

## 7. Health Endpoint Error Handling

**Priority: Medium**

### Required work
- Review `backend/app/api/settings.py`.
- Avoid exposing raw internal exceptions or sensitive configuration details through public health responses.
- Log detailed errors privately.
- Return safe, useful status information to the frontend.

## 8. Audit Hardcoded and Static Data

**Priority: High**

Review all major frontend and backend screens for hardcoded or placeholder data.

Areas to inspect:
- Dashboard KPIs and charts.
- Suppliers, orders, products, shipments, and inventory.
- Impact analysis.
- Recovery simulations.
- Decision reports.
- Replay functionality.
- Memory Centre.
- API URLs, IDs, organization references, confidence values, and estimates.

Requirements:
- API mode must use actual backend data.
- Mock data must remain isolated to explicit mock/demo mode.
- Static strategy templates and legitimate fallback rules may remain where appropriate.
- Do not replace unavailable backend information with fabricated values.

## 9. Automated Testing

**Priority: High**

### Backend
- Run the complete existing backend test suite.
- Add tests for SKU matching and outcome provenance.
- Add organization and supplier isolation tests.
- Test error handling and AI provider failures.
- Test memory retention and retrieval.

### Frontend
- Run lint and production build.
- Test API-mode workflows.
- Test loading, empty, and error states.
- Verify that the UI handles slow AI responses correctly.

### End-to-end
Test the complete workflow:

1. Report a crisis.
2. Generate impact analysis.
3. Run recovery simulations.
4. Generate a decision report.
5. Record a decision.
6. Record its outcome.
7. Verify that the outcome is retained in memory.
8. Report a similar crisis.
9. Verify that relevant historical evidence is retrieved.

## 10. Documentation Updates

Review and update:
- `README.md`
- `FRONTEND_API_CONTRACT.md`
- `frontend/FRONTEND_INTEGRATION.md`

Ensure documentation reflects the actual implementation, API endpoints, request/response formats, setup steps, environment variables, and complete workflow.

## 11. Hackathon Requirement Verification

Verify the official hackathon requirements, including any Band Desktop/SDK requirement mentioned in the project prompt.

Do not add a new integration based only on an assumption. First confirm whether it is an official requirement and document the evidence.

## 12. Recommended Implementation Order

1. Correct SKU and inventory matching.
2. Correct outcome provenance.
3. Fix AI recommendation timeout and retry behaviour.
4. Secure demo memory reset operations.
5. Sanitize health endpoint errors.
6. Complete the hardcoded-data audit.
7. Add and run automated tests.
8. Update documentation.
9. Verify all official hackathon requirements.
10. Perform a complete end-to-end test.

## 13. Final Completion Checklist

- [ ] Inventory matching is accurate and tested.
- [ ] Outcome provenance is correct.
- [ ] Historical memory is preserved.
- [ ] AI recommendations handle slow responses safely.
- [ ] Demo reset operations are protected.
- [ ] Health endpoint errors are sanitized.
- [ ] API mode does not rely on fabricated business data.
- [ ] Organization-level data isolation is tested.
- [ ] Backend tests pass.
- [ ] Frontend lint and build pass.
- [ ] End-to-end workflow passes.
- [ ] Documentation matches the implementation.
- [ ] Official hackathon requirements are verified.

**Important:** Make changes incrementally. Do not rewrite working modules unnecessarily. Report any unresolved issues, external provider limitations, or incomplete requirements rather than marking them as completed.