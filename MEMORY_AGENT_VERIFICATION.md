# MEMORY_AGENT_VERIFICATION.md

## Implementation evidence

- Agent: `backend/app/services/agent.py` — `AgentService` uses Groq (`settings.groq_model`) with OpenAI-compatible tool calling (`tool_choice="auto"`), up to `agent_max_tool_iterations`.
- Memory: `backend/app/services/memory.py` wraps official `hindsight-client`; retain/recall/reflect against `settings.hindsight_base_url`.
- Tools: `backend/app/services/tools.py` exposes 15 validated, org-scoped tools (supplier profile/history/reliability, orders, shipment events, bottlenecks, compare, alerts, contingency, create/update order, followups, retrieve/retain memory, reflect).
- API: `backend/app/api/agent.py` `/agent/chat`, `/agent/runs`, `/agent/conversations`.
- Persistence: PostgreSQL via SQLAlchemy; conversations/messages/agent_runs/memory_operation_logs/memory_records.

## Hindsight smoke (executed)

Command: `backend\.venv\Scripts\python.exe scripts/smoke_hindsight.py` and `smoke_reflect.py`
Result: retain ok (success=True, bank smoke_test_bank_001), recall 6 results, reflect completed in ~1.0s/18.0s. Console failures were Windows cp1252 Unicode printing only, not service errors.

## Agent flow

`AgentService.run` automatically calls `memory_service.recall` (and `reflect` for recommendation questions) before LLM call, injects memory block into system prompt, records memory_hits/reflect_answer in `AgentRun.evidence` and `tool_calls` traces (actual LLM tool calls).

## Status

Core memory-powered agent is implemented and wired. Full end-to-end scenario (A–M) requires authenticated DB seed + multi-user/org setup; backend starts successfully on :8000. Hindsight retain/recall/reflect verified live.
