# MASTER BUILD PROMPT — SUPPLYMIND

## Persistent-Memory Supply Chain Intelligence Using Hindsight

You are a principal software architect, senior full-stack engineer, AI agent engineer, database architect, DevOps engineer and quality assurance engineer.

Your task is to design, implement, run, test and document a complete application named SUPPLYMIND.

You are not being asked to produce a proposal, mockup, architecture diagram or superficial chatbot.

You must build a functional, locally runnable application with a genuine persistent Hindsight memory engine, real AI tool calling, working business workflows, a professional frontend, Band coordination and automated tests.

The central objective is to demonstrate that an AI agent becomes more useful, personalized and accurate at supply-chain decisions as it accumulates verified organizational experiences.

Do not claim that the application works unless you have actually run and tested it.

---

# PART 1 — HACKATHON COMPLIANCE

Follow the official Hindsight hackathon problem statement and content submission guide.

Mandatory requirements:

1. Use Hindsight by Vectorize as the actual persistent agent memory.
2. Demonstrate genuine retain, recall and reflect operations.
3. Demonstrate memory improvement over multiple interactions.
4. Use a genuine LLM with tool/function calling.
5. Download and use Band AI Desktop.
6. Build a real business application, not a generic chatbot.
7. Use realistic synthetic business data.
8. Demonstrate memory across separate conversations and application restarts.
9. Build a professional interactive application.
10. Document how Hindsight is integrated.

Read these sources before implementing:

- https://hindsight.vectorize.io/
- https://github.com/vectorize-io/hindsight
- https://docs.hindsight.vectorize.io/
- https://www.band.ai/hacker-guide
- https://docs.band.ai/
- https://console.groq.com/docs/tool-use/overview
- https://console.groq.com/docs/models

Read the installed Hindsight documentation skill if available.

Use current official documentation as the authority for API methods, SDK versions, configuration, Docker setup and Band adapters.

Do not invent SDK methods, configuration variables, integration interfaces or API arguments.

If a requested integration is unsupported, explain the limitation and implement the closest officially supported alternative.

Do not silently substitute an ordinary database or conversation history for Hindsight.

## Judging priorities

Build specifically to demonstrate:

- Innovation: 30%
- Hindsight memory: 25%
- Technical implementation: 20%
- User experience: 15%
- Real-world impact: 10%

Memory must be the central differentiator.

---

# PART 2 — PRODUCT VISION

SUPPLYMIND is an organizational-memory-powered supply-chain intelligence platform.

It remembers historical supplier relationships, orders, delivery performance, transportation incidents, complaints, operational preferences and previous procurement decisions.

It uses these experiences to make better future recommendations.

Central principle:

"An ordinary supply-chain system tracks what is happening. SUPPLYMIND remembers what happened, learns from it and uses that experience to anticipate what could happen next."

Target users:

- Procurement managers
- Supply-chain managers
- Logistics managers
- Operations managers
- Inventory planners

The system should feel like an experienced procurement and supply-chain analyst who has worked with the company for years.

It should understand the company's history without requiring users to repeat themselves.

Memory must belong to the organization, not an individual chatbot session.

It must survive:

- Browser refreshes.
- Application restarts.
- New conversations.
- Different users in the same organization.
- Multiple days of operation.

---

# PART 3 — TECHNOLOGY STACK

Use the following preferred stack.

Backend:
- Python 3.11+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Hindsight Python SDK: hindsight-client
- Groq Python SDK
- Band Python SDK
- APScheduler or a reliable database-backed scheduler.

Frontend:
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts
- Lucide icons.

Infrastructure:
- Docker Compose
- PostgreSQL
- Hindsight
- Redis only if justified by the actual architecture.
- Environment variables.
- Automated database migrations.

## Runtime LLM

Use Groq as the primary inference provider.

Preferred model:

openai/gpt-oss-120b

Make the model configurable through environment variables.

Do not use deprecated Groq models.

Support a configurable fallback model if available.

Implement:
- Tool/function calling.
- Tool argument validation.
- Invalid JSON recovery.
- Maximum tool iteration limits.
- Timeouts.
- Retries with exponential backoff.
- Rate-limit handling.
- Graceful provider failures.

Never assume free-tier API access is unlimited.

## Hindsight hosting

Prefer self-hosted Hindsight using the official Docker deployment.

Configure its internal LLM separately from the application's runtime LLM.

Groq may be used as the Hindsight LLM provider if supported by the current documentation.

If Groq is unavailable, use another officially supported provider.

Document the local inference alternative where appropriate.

Do not assume that configuring GROQ_API_KEY for the application automatically configures Hindsight.

Read the actual Hindsight deployment documentation before implementing Docker configuration.

Preserve memory data across restarts using persistent storage.

## Band

Use Band Desktop for coding-agent coordination.

Where appropriate, use the official Python Band SDK for in-product agents.

Do not invent adapter names or SDK arguments.

Read the current official Band SDK documentation before implementation.

---

# PART 4 — CORE APPLICATION MODULES

## MODULE A — EXECUTIVE DASHBOARD

Create a professional supply-chain dashboard.

Show:

1. Total active orders.
2. Delivered orders.
3. Delayed orders.
4. At-risk orders.
5. Average delivery delay.
6. Supplier reliability.
7. Upcoming deliveries.
8. Pending alerts.
9. Critical bottlenecks.
10. Recent agent decisions.

Charts:

- On-time versus delayed deliveries.
- Supplier reliability comparison.
- Delivery-delay trends.
- Order status distribution.
- Historical supplier performance.
- Risk distribution.

Every metric must come from database records.

Never hardcode dashboard statistics after initial seeding.

Clearly label synthetic demonstration data.

## MODULE B — SUPPLIER INTELLIGENCE

Implement supplier CRUD and detailed supplier profiles.

Supplier attributes:

- Supplier ID.
- Name.
- Contact information.
- Location.
- Product categories.
- Historical orders.
- Promised delivery times.
- Actual delivery times.
- Average delay.
- On-time delivery rate.
- Quality complaints.
- Communication complaints.
- Transportation incidents.
- Reliability history.
- Risk assessment.

When asked:

"Should we order from Supplier Alpha?"

The agent must:

1. Identify the supplier.
2. Retrieve relevant Hindsight memories.
3. Retrieve structured supplier records.
4. Calculate historical delivery metrics.
5. Examine previous complaints.
6. Consider the new order's requirements.
7. Compare alternative suppliers.
8. Produce an evidence-backed recommendation.

Example historical dataset:

Order 101: Expected 5 days, actual 15 days.
Order 102: Expected 7 days, actual 12 days.
Order 103: Expected 5 days, actual 13 days.

Calculate metrics using actual database data.

Do not let the LLM calculate authoritative business metrics by guessing.

Clearly distinguish historical facts from predictions.

Do not make unverified allegations about suppliers.

## MODULE C — ORDER MANAGEMENT

Implement complete CRUD functionality.

Order fields:

- Order ID.
- Company ID.
- Supplier ID.
- Product.
- Quantity.
- Order date.
- Promised delivery date.
- Estimated arrival date.
- Actual arrival date.
- Status.
- Priority.
- Destination.
- Transportation mode.
- Tracking reference.
- Financial impact.
- Related incidents.

Statuses:

- Created.
- Confirmed.
- Processing.
- Dispatched.
- In transit.
- Delayed.
- Delivered.
- Cancelled.

The agent can inspect, create and update orders through validated backend tools.

Every operation must be persisted.

Never fabricate shipment updates.

## MODULE D — HINDSIGHT MEMORY ENGINE

This is the highest-priority module.

Use the actual Hindsight Python SDK.

Implement genuine:

- retain
- recall
- reflect

Do not create mock functions that merely log these operation names.

### Memory types

Organize memory conceptually into:

A. Episodic memory

Individual historical experiences:

- Delivery delays.
- Damaged shipments.
- Quantity discrepancies.
- Supplier complaints.
- Transportation incidents.
- Successful mitigation actions.

B. Semantic memory

Consolidated organizational knowledge:

- Supplier performance patterns.
- Common transportation problems.
- Product-specific risks.
- Historical supplier reliability.
- Repeated operational bottlenecks.

C. Decision memory

- Previous supplier selections.
- Procurement decisions.
- Reasons behind decisions.
- Approved alternatives.
- Previous recommendations.

D. Outcome memory

- Whether recommendations worked.
- Whether an alternative supplier succeeded.
- Actual delivery outcomes.
- Whether an intervention reduced a delay.
- Whether a previous decision caused problems.

E. Preference memory

- Preferred delivery buffers.
- Critical product priorities.
- Supplier selection preferences.
- Escalation preferences.
- Operational constraints.

F. Future-action memory

- Follow-up deadlines.
- Supplier confirmations.
- Upcoming delivery checkpoints.
- Escalations.
- Pending procurement decisions.

### Actual memory lifecycle

Implement:

1. Extract meaningful facts from user input and business events.
2. Validate those facts against structured business records.
3. Assign provenance and confidence.
4. Retain verified and appropriately attributed information in Hindsight.
5. Retrieve relevant memories during future conversations.
6. Use Hindsight reflect for contextual reasoning.
7. Incorporate retrieved knowledge into the runtime agent's decision.
8. Record new decisions and outcomes.
9. Update organizational knowledge through subsequent interactions.

Do not retain every sentence.

Do not retain hallucinations.

Do not turn an inference into a verified fact.

Track source, event timestamp, supplier ID, order ID and company ID wherever supported.

Maintain a clear distinction between:

- Verified business facts.
- User-reported facts.
- Imported external observations.
- AI inferences.
- Recommendations.

Implement correction workflows when historical information is wrong.

### Memory provenance

Every memory-backed recommendation should expose:

- Memory or source reference where available.
- Related supplier.
- Related order.
- Event date.
- Source type.
- Whether the claim is verified or inferred.

Build a memory inspection interface.

Users should be able to see what the agent remembers and why.

### Multi-company isolation

Every company must have an independent Hindsight memory bank.

Use a stable, server-generated bank ID mapped to the authenticated company.

Never allow users to provide arbitrary memory bank IDs through the frontend.

Enforce tenant isolation on every API request.

Test that Company A cannot retrieve Company B's memories.

Do not rely on frontend filtering for security.

---

# PART 5 — MEMORY LEARNING LABORATORY

This is the signature feature of SUPPLYMIND.

Build a dedicated interface named:

MEMORY LEARNING LAB

Its purpose is to prove that Hindsight improves the agent's recommendations as organizational experience accumulates.

Do not merely display the number of stored memories.

Demonstrate actual behavioral improvement.

## Experiment design

Create a repeatable evaluation scenario involving:

- Multiple suppliers.
- Historical delivery delays.
- Quality complaints.
- Supplier communication issues.
- Previous procurement decisions.
- Delivery outcomes.
- Transportation disruptions.
- Company-specific preferences.

Create at least 20 realistic synthetic business interactions.

Retain their meaningful information through actual Hindsight operations.

Test the same procurement questions at different memory stages:

- Stage 0: No relevant memories.
- Stage 1: Initial experiences.
- Stage 5: Five interactions.
- Stage 10: Ten interactions.
- Stage 20: Twenty interactions.

Allow the user to reset or replay the synthetic experiment.

Reset must only affect the demo company's test memory bank and associated test records.

Never delete production memories accidentally.

## Before-and-after evaluation

Use the same:

- Base model.
- User question.
- Structured business records.
- Business rules.
- Evaluation dataset.

Compare:

A. Memory-disabled response.

B. Memory-enabled response.

Display:

- Recommendation.
- Relevant historical evidence.
- Number of relevant memories retrieved.
- Supplier performance metrics.
- Risk factors identified.
- Personalization.
- Missing information.
- Evidence coverage.

Implement a reproducible evaluation rubric.

Suggested scoring dimensions:

1. Historical evidence relevance.
2. Supplier-risk identification.
3. Correctness of business calculations.
4. Preference adherence.
5. Decision consistency.
6. Evidence-backed reasoning.

Calculate scores using a documented evaluation method.

Do not fabricate scores or claim that accuracy improved without test results.

Use a fixed evaluation dataset and a transparent rubric.

Where possible, include human-reviewed expected answers.

## Memory growth visualization

Show:

- Number of retained memories.
- Memory categories.
- Recall operations.
- Reflect operations.
- Memory retrieval history.
- Interaction count.
- Recommendation evolution.
- Evaluation results over time.

Add a timeline showing when the agent learned each important supplier fact.

The dashboard must make the learning process understandable within 60 seconds.

## Critical requirement

A new conversation must still benefit from experiences retained during previous conversations.

Demonstrate this explicitly.

---

# PART 6 — AGENT WORKFLOWS

Implement a controlled agent architecture.

Prefer a LangGraph stateful workflow if appropriate, but do not introduce unnecessary complexity.

The system must have a primary orchestrator and specialized agents.

## Agent 1 — Procurement Intelligence Agent

Responsibilities:

- Understand procurement requests.
- Retrieve supplier memories.
- Examine historical orders.
- Compare suppliers.
- Recommend purchasing strategies.

## Agent 2 — Supplier Intelligence Agent

Responsibilities:

- Analyze supplier history.
- Identify reliability patterns.
- Review complaints.
- Calculate supplier metrics.
- Maintain supplier knowledge.

## Agent 3 — Logistics and Monitoring Agent

Responsibilities:

- Monitor shipment status.
- Detect delayed shipments.
- Identify bottlenecks.
- Evaluate transportation disruptions.
- Recommend contingency routes or alternatives.

## Agent 4 — Risk Analysis Agent

Responsibilities:

- Assess order risk.
- Detect supplier concentration.
- Identify critical inventory dependencies.
- Evaluate potential disruption impact.
- Produce explainable risk assessments.

## Agent 5 — Memory Agent

Responsibilities:

- Extract useful memories.
- Retain verified experiences.
- Recall historical knowledge.
- Invoke reflect.
- Maintain memory provenance.
- Support memory inspection.

## Agent 6 — Orchestrator

Responsibilities:

- Understand user intent.
- Route tasks.
- Coordinate specialists.
- Combine evidence.
- Validate decisions.
- Return final recommendations.

Avoid unnecessary agents that only generate separate paragraphs.

Every agent must have a clear responsibility.

---

# PART 7 — BAND COORDINATION

Band must be used meaningfully.

Do not treat installing Band Desktop as sufficient proof of integration.

## Coding-agent coordination

Use Band Desktop to coordinate the coding team:

- Planner.
- Backend developer.
- Frontend developer.
- QA/reviewer.

Give each coding agent a clear role.

Use separate work ownership and review changes before merging.

Do not let multiple agents overwrite the same files without coordination.

## In-product coordination

Where supported by the current Band Python SDK, register the actual SUPPLYMIND agents as separate Band agents.

Use a shared project room.

Demonstrate a meaningful workflow:

1. Procurement agent receives an order request.
2. It requests historical supplier information from the supplier agent.
3. Risk agent evaluates the potential bottleneck.
4. Logistics agent evaluates delivery implications.
5. The agents share their findings through Band.
6. The orchestrator prepares the final recommendation.
7. A human procurement manager approves or rejects the decision.

Use genuine Band agent identities and supported room coordination.

Do not simulate agent communication with hardcoded transcripts.

Keep Band integration optional at application startup so that the core application still runs when Band credentials are not configured.

Document the setup.

The application must clearly distinguish Hindsight memory from Band's room conversation history.

Band coordination is not a substitute for Hindsight.

---

# PART 8 — PROACTIVE ORDER MONITORING

Create a persistent monitoring system.

When an order is created:

1. Save it to PostgreSQL.
2. Calculate the expected delivery date.
3. Retrieve relevant supplier memories.
4. Calculate a suitable monitoring schedule.
5. Create persistent scheduled actions.
6. Monitor shipment updates.
7. Trigger appropriate alerts.
8. Escalate unresolved risks.

Example:

Expected delivery: November 20.

Historical average delay: 7 days.

The agent may recommend an earlier checkpoint on November 12.

This is a risk-management checkpoint, not a guaranteed delivery prediction.

Implement:

- Upcoming delivery alerts.
- Supplier confirmation reminders.
- Delayed shipment alerts.
- Overdue order alerts.
- Critical bottleneck notifications.
- Escalation history.

Use database-backed scheduling.

Jobs must survive application restarts.

Implement idempotency to prevent duplicate notifications.

Do not depend on a browser being open.

For the prototype, notifications can be displayed inside the application.

Email integration may be optional.

---

# PART 9 — BOTTLENECK DETECTION

Identify bottlenecks using:

- Overdue orders.
- Delayed shipments.
- Repeated supplier failures.
- Critical inventory shortages.
- Multiple orders depending on one supplier.
- Transportation disruptions.
- Unconfirmed deliveries.
- Quality failures.
- Supplier communication failures.

For each bottleneck, show:

1. Affected orders.
2. Affected supplier.
3. Severity.
4. Historical supporting evidence.
5. Potential business impact.
6. Recommended intervention.
7. Alternative suppliers or routes, if verified alternatives exist.

Use deterministic business rules for authoritative calculations.

The LLM may explain the findings but must not invent the underlying data.

---

# PART 10 — WHAT-IF SIMULATION

Build a basic supply-chain disruption simulator.

Allow a manager to ask:

"What happens if Supplier Alpha cannot deliver for another 10 days?"

The system should:

1. Retrieve relevant supplier memories.
2. Identify affected orders.
3. Examine inventory dependencies.
4. Estimate possible delivery impact.
5. Identify alternative suppliers.
6. Suggest contingency actions.
7. Explain assumptions and uncertainty.

Clearly label simulated scenarios.

Never present hypothetical outputs as actual shipment information.

---

# PART 11 — DATABASE DESIGN

Design normalized PostgreSQL tables.

At minimum:

- organizations
- users
- memberships
- suppliers
- purchase_orders
- shipment_events
- supplier_complaints
- quality_incidents
- procurement_decisions
- decision_outcomes
- inventory_items
- inventory_movements
- alerts
- scheduled_actions
- conversations
- agent_runs
- memory_operation_logs
- evaluation_runs
- evaluation_results
- audit_logs

Use UUID primary keys where appropriate.

Implement:

- Foreign keys.
- Unique constraints.
- Indexes.
- Database migrations.
- Created and updated timestamps.
- Company-level ownership.
- Audit trails.

Never store API credentials in ordinary business tables.

Never treat the memory-operation log as a replacement for Hindsight.

---

# PART 12 — API DESIGN

Create versioned REST APIs.

Suggested endpoints:

Authentication:
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

Dashboard:
- GET /api/v1/dashboard/overview
- GET /api/v1/dashboard/analytics

Suppliers:
- GET /api/v1/suppliers
- POST /api/v1/suppliers
- GET /api/v1/suppliers/{id}
- PATCH /api/v1/suppliers/{id}
- DELETE /api/v1/suppliers/{id}

Orders:
- GET /api/v1/orders
- POST /api/v1/orders
- GET /api/v1/orders/{id}
- PATCH /api/v1/orders/{id}
- DELETE /api/v1/orders/{id}

Agent:
- POST /api/v1/agent/chat
- GET /api/v1/agent/conversations
- GET /api/v1/agent/runs/{id}

Memory:
- POST /api/v1/memory/retain
- POST /api/v1/memory/recall
- POST /api/v1/memory/reflect
- GET /api/v1/memory/overview
- GET /api/v1/memory/history
- GET /api/v1/memory/{id}

Learning laboratory:
- POST /api/v1/lab/seed
- POST /api/v1/lab/run
- GET /api/v1/lab/results
- POST /api/v1/lab/reset

Alerts:
- GET /api/v1/alerts
- PATCH /api/v1/alerts/{id}
- GET /api/v1/alerts/upcoming

Implement appropriate authentication, authorization, validation and error handling.

The API list is a starting point. Adapt it to the actual implementation.

---

# PART 13 — AGENT TOOL/FUNCTION CALLING

Create real backend tools.

Examples:

- get_supplier_profile
- get_supplier_order_history
- calculate_supplier_reliability
- get_order_details
- create_purchase_order
- update_order_status
- get_shipment_events
- identify_bottlenecks
- compare_suppliers
- retrieve_company_memory
- retain_business_experience
- reflect_on_supplier_history
- create_followup
- list_pending_alerts
- evaluate_contingency_options

Each tool must have:

- Validated inputs.
- Typed outputs.
- Authorization checks.
- Error handling.
- Logging.
- Tests.

The LLM cannot directly execute arbitrary SQL.

The LLM cannot bypass backend authorization.

The LLM cannot fabricate successful tool results.

Implement a robust multi-turn tool-calling loop using the official Groq SDK.

Handle malformed function arguments and repeated tool-call loops.

Set a maximum number of tool iterations.

Require human approval for consequential operations.

---

# PART 14 — USER INTERFACE

Build a polished enterprise application.

Suggested navigation:

1. Overview
2. Orders
3. Suppliers
4. Shipment Tracking
5. Bottleneck Analysis
6. AI Procurement Assistant
7. Memory Learning Lab
8. Organizational Memory
9. Alerts
10. Settings

## AI chat interface

Create a professional conversational interface.

Show:

- Agent responses.
- Tool activity.
- Retrieved memory references.
- Supplier evidence.
- Relevant order records.
- Risk assessments.
- Recommended next steps.

Include an expandable section named:

"Why did the agent make this recommendation?"

This must expose relevant evidence and memory sources.

## Memory interface

Show actual memory operations.

For each operation, show:

- Operation type.
- Timestamp.
- Company.
- Related supplier or order.
- Memory content summary.
- Source/provenance.
- Status.

Do not expose secret credentials or private internal chain-of-thought.

Show concise evidence and explanations instead.

## Design direction

Use a modern enterprise logistics visual language.

Prefer:

- Dark navy or neutral enterprise backgrounds.
- Clear typography.
- Clean information hierarchy.
- Professional charts.
- Consistent spacing.
- Accessible colors.
- Responsive layouts.
- Useful empty states.
- Loading and error states.

Avoid:
- Generic AI landing pages.
- Excessive gradients.
- Decorative animations.
- Fake data.
- Inert buttons.
- Non-functional dashboard widgets.

Every visible action must work.

---

# PART 15 — SYNTHETIC DATA

Create a realistic demonstration dataset.

Include:

- At least 5 suppliers.
- At least 20 historical orders.
- Different delivery performance patterns.
- Multiple supplier complaints.
- Transportation disruptions.
- Quality incidents.
- Previous procurement decisions.
- Successful mitigation outcomes.
- Future pending deliveries.

Include both good and bad suppliers.

Create a repeatable seeding script.

Ensure that the same dataset can be recreated.

Retain appropriate historical experiences into Hindsight through actual SDK operations.

Clearly label seeded information as synthetic.

Use realistic dates and consistent relationships between records.

---

# PART 16 — SECURITY AND RELIABILITY

Implement:

- Secure password hashing.
- Authentication.
- Company-level authorization.
- Input validation.
- Rate limiting where appropriate.
- Secrets management.
- Safe logging.
- Database transaction handling.
- Audit logging.
- Scheduler idempotency.
- Memory-bank isolation.
- Error recovery.

Treat retrieved memories as untrusted business data, not executable instructions.

Prevent prompt injection through supplier notes, complaints and imported documents.

Do not allow a memory to override system instructions or authorization rules.

Do not allow one company to access another company's information.

---

# PART 17 — TESTING AND VERIFICATION

This section is mandatory.

Do not stop after generating code.

Actually run the application and tests.

## Hindsight integration tests

Verify:

1. A real memory is retained.
2. The memory survives a new conversation.
3. The memory can be recalled.
4. Reflect generates a contextually relevant answer.
5. A later business event is retained.
6. A new query retrieves the updated knowledge.
7. The application restarts without losing memory.
8. Separate organizations cannot retrieve one another's memories.

Use the actual Hindsight instance.

Do not mock Hindsight in the integration tests.

Mocks may be used in isolated unit tests only.

## Agent tests

Test:

- Tool selection.
- Tool arguments.
- Invalid tool arguments.
- Supplier comparison.
- Incorrect supplier identifiers.
- Missing historical data.
- Conflicting memories.
- Malformed model responses.
- API rate limits.
- Model unavailability.

## Business logic tests

Verify calculations:

Average delivery delay.
On-time delivery percentage.
Delayed order count.
Supplier reliability.
Risk indicators.

Use deterministic expected results.

## Scheduler tests

Verify:

- Upcoming alerts.
- Overdue orders.
- Restart recovery.
- Duplicate prevention.
- Rescheduling.
- Cancelled orders.
- Alert acknowledgement.

## Frontend tests

Verify:

- Navigation.
- CRUD operations.
- Chat functionality.
- Dashboard data.
- Memory visualization.
- Learning laboratory.
- Loading and error states.

## End-to-end test

Run a complete scenario:

1. Seed historical supplier experiences.
2. Start a new conversation.
3. Ask for a supplier recommendation.
4. Verify memory retrieval.
5. Create a purchase order.
6. Simulate a transportation delay.
7. Trigger an alert.
8. Record the outcome.
9. Start another conversation.
10. Ask the same supplier question.
11. Verify that the recommendation incorporates the newly retained experience.

Produce a test report.

Do not mark a test as passed unless it actually ran successfully.

---

# PART 18 — DEMO EXPERIENCE FOR JUDGES

Create a guided demonstration mode.

The complete demonstration should take approximately 3–5 minutes.

## Demo story

Scenario:

A procurement manager needs 1,000 electronic components urgently.

The company has previously experienced supplier delays and quality issues.

### Act 1: The agent without memory

Ask:

"Which supplier should I choose for this urgent order?"

Show the baseline response.

### Act 2: Introduce organizational experience

Seed or retain:

- Previous delivery delays.
- Quality complaints.
- Supplier communication problems.
- A successful alternative supplier.
- Company procurement preferences.

Show actual Hindsight retain operations.

### Act 3: Ask the same question again

Start a fresh conversation.

Ask the same question.

Show actual Hindsight recall.

Show how the recommendation incorporates previous business experiences.

### Act 4: Demonstrate proactive intelligence

Create a new order.

Simulate a delay.

Show the monitoring system detecting the risk and generating a reminder.

### Act 5: Show learning

Retain the new shipment outcome.

Start another conversation.

Ask about the supplier again.

Show how the new experience influences future decisions.

The demo must be reproducible with synthetic data.

Never fake memory operation logs.

---

# PART 19 — CONTENT SUBMISSION REQUIREMENTS

The project must support the official content submission requirements.

Generate a submission guide in the repository.

Each team member must prepare:

1. An individual technical article.
2. An individual LinkedIn post.
3. One team video.

The content guide specifies public, linkable articles, individual social posts and a team video.

### Article

Create a prompt template that reads the actual project repository.

It should generate:
- Twenty possible technical article titles.
- One selected article.
- Real code snippets.
- Actual Hindsight integration details.
- Before-and-after behavior.
- Honest engineering lessons.

Do not invent implemented features or benchmark results.

The official guide contains conflicting word-count instructions: its overview says 800–1,500 words, while the detailed article prompt says 1,200–2,000 words. Use 800–1,500 words as the default submission target unless the organizers clarify otherwise.

Do not mention the word hackathon anywhere in the article or its title.

### LinkedIn post

Create a prompt template that generates a technically credible post.

Requirements:
- Under 800 characters.
- No mention of the hackathon.
- No hashtags in the first two lines.
- Three to five relevant hashtags at the end.
- Include the project GitHub link.
- Explain one concrete before-and-after behavior caused by Hindsight.

The first comment should link to the published article.

A subsequent comment should link to the official Hindsight repository.

### Team video

Generate a 2–5 minute demo script.

Structure:

1. Introduction.
2. The problem without memory.
3. Actual retain and recall demonstration.
4. Before-and-after recommendation.
5. Key engineering takeaway.

Include actual screen cues, endpoints and repository paths.

The published video must be public on YouTube.

Do not merely save it to Google Drive.

Generate a submission checklist.

---

# PART 20 — PROJECT DOCUMENTATION

Create:

README.md
ARCHITECTURE.md
MEMORY_DESIGN.md
AGENT_WORKFLOWS.md
BAND_SETUP.md
HINDSIGHT_SETUP.md
API_DOCUMENTATION.md
TESTING.md
DEMO_SCRIPT.md
SUBMISSION_CHECKLIST.md
.env.example

Document:

- Architecture.
- Database relationships.
- Hindsight memory lifecycle.
- Memory-bank isolation.
- Agent responsibilities.
- Band integration.
- Environment variables.
- Local startup commands.
- Test commands.
- Synthetic data generation.
- Demo instructions.
- Known limitations.

Never include real API keys in documentation or Git history.

---

# PART 21 — DEVELOPMENT EXECUTION PLAN

Work in the following order.

Phase 1: Repository inspection and planning.

- Read the requirements.
- Inspect current documentation.
- Verify SDK compatibility.
- Create architecture.
- Identify implementation risks.
- Produce an ordered task plan.

Phase 2: Infrastructure.

- Create backend.
- Create frontend.
- Configure PostgreSQL.
- Configure Hindsight.
- Configure migrations.
- Verify services.

Phase 3: Core business logic.

- Supplier management.
- Order management.
- Shipment events.
- Supplier metrics.
- Bottleneck detection.

Phase 4: Hindsight integration.

- Create company memory banks.
- Implement retain.
- Implement recall.
- Implement reflect.
- Implement provenance.
- Test persistence.
- Test tenant isolation.

Phase 5: Agent implementation.

- Implement tool calling.
- Implement agent orchestration.
- Implement specialist workflows.
- Implement Band coordination.

Phase 6: Proactive monitoring.

- Implement persistent jobs.
- Implement notifications.
- Implement escalation.

Phase 7: Frontend.

- Dashboard.
- Orders.
- Suppliers.
- AI assistant.
- Memory laboratory.
- Memory inspection.
- Alerts.

Phase 8: Testing.

- Unit tests.
- Integration tests.
- End-to-end tests.
- Memory improvement evaluation.
- Security tests.

Phase 9: Demo and documentation.

- Seed dataset.
- Demo workflow.
- Screenshots.
- Architecture documentation.
- Submission templates.

Do not attempt to implement every module simultaneously.

Prioritize the actual memory engine and one complete end-to-end procurement workflow before optional functionality.

---

# PART 22 — STRICT DEVELOPMENT RULES

1. Do not generate a frontend-only prototype.
2. Do not fake Hindsight operations.
3. Do not use ordinary chat history as persistent memory.
4. Do not replace Hindsight with a vector database.
5. Do not hardcode dashboard metrics.
6. Do not fabricate supplier histories.
7. Do not invent SDK methods.
8. Do not claim tests passed without executing them.
9. Do not leave essential buttons non-functional.
10. Do not expose API credentials.
11. Do not mix organizational memories.
12. Do not allow unauthorized autonomous purchasing.
13. Do not claim predictions are guaranteed.
14. Do not claim accuracy improvements without evaluation.
15. Do not silently skip required integrations.

If a feature cannot be completed, clearly document what is missing and why.

Never hide errors behind fake success messages.

If a provider is unavailable, use a documented fallback.

If the implementation encounters a technical issue, investigate it, fix it and rerun the relevant tests.

Do not ask the user to make unnecessary architectural decisions. Choose sensible defaults and explain important trade-offs.

Keep the code modular and maintainable.

---

# PART 23 — DEFINITION OF DONE

SUPPLYMIND is complete only when:

- The frontend starts successfully.
- The backend starts successfully.
- PostgreSQL persists business data.
- Hindsight starts successfully.
- Genuine retain, recall and reflect calls work.
- Memory survives separate conversations.
- Memory survives backend restarts.
- Supplier recommendations use historical memories.
- Order and supplier CRUD work.
- The monitoring system generates persistent alerts.
- The memory learning laboratory runs a reproducible experiment.
- The same question produces evidence-backed memory-aware recommendations.
- The application distinguishes facts from inferences.
- Company memory isolation is tested.
- Band Desktop has been used for development coordination.
- The supported Band integration works if configured.
- Automated tests pass.
- Documentation is complete.
- The demo can be reproduced.

---

# FINAL INSTRUCTION

Start by inspecting the official documentation and verifying the current SDKs and integrations.

Then create the project plan and begin implementation.

Do not stop at the planning stage.

Build the actual application, start the services, execute the tests, inspect the results, fix failures and verify the complete end-to-end workflow.

Your ultimate objective is:

Build an AI supply-chain intelligence system that does not merely answer questions using current data, but becomes increasingly useful by remembering the organization's actual experiences and learning from the outcomes of its previous decisions.

Make Hindsight memory the heart of the product.

Make the improvement visible.

Make the implementation real.

Build SUPPLYMIND.