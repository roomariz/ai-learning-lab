# Production Agent Hardening Checklist

This checklist complements `docs/stateful_agent_blueprint.md`.

The blueprint teaches the core architecture for stateful LangGraph agents: structured state, framework-managed runtime access, explicit state mutation with `Command(update={...})`, thread-based persistence, and clean separation between agent, tools, state, checkpointer, and UI.

This document covers the additional controls needed before a stateful agent is treated as production-ready.

---

## Minimum Production Gate

An agent must not handle production users until these blocking controls exist:

- Durable persistence using a production-appropriate backend. Use `PostgresSaver` or another managed durable store for multi-process production systems. Use `SqliteSaver` only for local, single-process, or small controlled deployments where its limits are understood. Do not use `MemorySaver` for production state.
- Idempotency protection for every state-changing or external side-effecting tool.
- Concurrency control for shared threads and tenant-owned resources.
- Tenant isolation and role-based access control enforced outside the model.
- Secure secrets handling, encryption at rest where state is sensitive, and least-privilege production tool credentials.
- Human approval for irreversible or high-risk actions.

Before general availability, all of the following must also exist:

- Explicit state schema versioning with tested migrations.
- Defined resume behaviour for interrupted threads after deploys, graph changes, prompt changes, tool changes, and state migrations.
- Input validation, tool-argument validation, and output validation.
- Model-level controls, including pinned model versions, bounded token limits, structured outputs where appropriate, and deterministic parsing for critical decisions.
- Key rotation for secrets and encrypted state.
- Prompt injection and tool injection protections with adversarial tests.
- Audit trails for state-changing actions.
- Timeouts, bounded retries, backoff, and circuit breakers for dependencies.
- Graceful degradation paths for rate limits, quota exhaustion, dependency failures, and partial tool failures.
- Structured logs, trace IDs, correlation IDs, metrics, and production alerts.
- Redaction rules for logs and traces.
- Retention, deletion, backup, and restore procedures.
- Rate limits, quotas, and cost controls.
- Separate local, staging, and production environments.
- A rollout and rollback plan using canaries or feature flags for risky changes.
- Automated tests and evals covering state transitions, migrations, regression fixtures, adversarial cases, tool routing, and model-output quality thresholds.

---

## Build-Time Controls

### Durable Persistence

- Use a durable checkpointer appropriate for the deployment model.
- Prefer `PostgresSaver` or another managed durable backend for production systems that run across multiple workers, containers, or processes.
- Use `SqliteSaver` only for local development, single-process deployments, prototypes, or constrained internal tools where file locking, backup, and scaling limits are acceptable.
- Do not use `MemorySaver` for production state.
- Store state in a managed location with documented backup, restore, monitoring, encryption, and access controls.
- Treat `thread_id` as a stable production identifier, not a demo string.
- Prevent users from selecting or guessing another user's `thread_id`.

### State Schema Versioning And Migrations

- Add an explicit schema version to persisted state.
- Keep migrations deterministic, tested, and reversible where possible.
- Validate state after loading and after migration.
- Define the behaviour for unknown, missing, or future schema versions.
- Keep old regression fixtures for representative state snapshots.
- Make migrations safe for threads that are paused, interrupted, or resumed after a deploy.

### Resume Behaviour Across Deploys

- Define what happens when a thread resumes after graph code, prompts, tools, model settings, or state schema have changed.
- Version graph definitions, prompts, tool contracts, and model settings alongside state schemas.
- Decide which in-flight threads can continue, which must migrate, and which must fail closed with a recovery path.
- Test resume from checkpoints created by the previous production version.
- Keep rollback compatible with recently written checkpoints where practical.

### Idempotency And Duplicate Tool-Call Protection

- Assign idempotency keys to state-changing requests and tool calls.
- Persist completed tool-call IDs and results so retries do not repeat side effects.
- Make external writes safe to retry, especially payments, tickets, emails, orders, and account changes.
- Return the previous successful result when the same idempotency key is replayed.
- Store enough metadata to distinguish a genuine retry from a conflicting request using the same key.

### Concurrency Control And Optimistic Locking

- Protect concurrent updates to the same thread or tenant-owned resource.
- Use revision numbers, timestamps, compare-and-swap writes, database transactions, or row-level locks.
- Detect stale writes and retry with a fresh state read where safe.
- Decide which operations must be serialised rather than merged.
- Test simultaneous invocations against the same thread.

### Input Validation And Output Validation

- Validate user input before agent invocation.
- Validate tool arguments against typed schemas.
- Validate tool outputs before adding them to state or exposing them to the user.
- Reject malformed, oversized, unsupported, or unsafe payloads early.
- Prefer allow-lists for commands, enum values, file types, domains, and tool targets.
- Validate final agent output for required structure, policy constraints, and user-visible safety.

### Model-Level Controls

- Pin production model versions or define an explicit model upgrade process.
- Set per-call max token limits, timeout limits, and cost ceilings.
- Use structured outputs, JSON schemas, constrained decoding, or deterministic parsers for critical routing and state-changing decisions.
- Keep temperature and sampling settings deliberate and versioned.
- Record model name, model version, prompt version, and decoding settings in traces.
- Test fallback models before enabling them in production.

### Tenant Isolation And Role-Based Access Control

- Scope every thread, state record, tool call, and external resource to a tenant or account.
- Enforce tenant checks in application code and storage queries.
- Apply role-based access control before invoking tools or exposing state.
- Keep authorisation checks outside the model.
- Test cross-tenant access attempts directly.

### Secrets, Encryption, And Least-Privilege Tools

- Keep secrets in a secret manager or environment-specific configuration, never in prompts, state, logs, traces, or fixtures.
- Encrypt sensitive persisted state at rest.
- Define key ownership, key rotation, thread-level or tenant-level encryption strategy, and recovery procedures.
- Give each tool the minimum credentials and permissions needed.
- Separate read-only tools from state-changing tools.
- Rotate credentials and encryption keys on a documented schedule and after suspected exposure.
- Disable unused tools in production.

### Prompt Injection And Tool Injection Protection

- Treat user content, retrieved documents, web pages, emails, tickets, and tool outputs as untrusted.
- Keep tool routing and authorisation outside the model wherever possible.
- Do not let untrusted content override system instructions, developer instructions, approval rules, or access controls.
- Constrain tool inputs with schemas, allow-lists, and policy checks.
- Add adversarial tests for instructions hidden in retrieved content and tool responses.

### Human Approval For Irreversible Or High-Risk Actions

- Require approval for irreversible, high-cost, privileged, destructive, financial, external, or user-impacting actions.
- Store approval requests and decisions with enough context for audit.
- Re-check permissions at approval time, not only when the request is created.
- Expire stale approvals.
- Make denial and timeout paths explicit.

---

## Deploy-Time Controls

### Environment Separation

- Keep local, staging, and production environments separate.
- Use separate state stores, secrets, API keys, tools, model configurations, and external integrations.
- Block production tools from local demos and tests unless explicitly approved.
- Seed staging with synthetic or redacted data.
- Make environment names visible in logs, traces, dashboards, and admin tooling.

### Rollout Strategy

- Release risky changes behind feature flags.
- Use canary deployments for new graphs, tools, prompts, migrations, model versions, and checkpoint backends.
- Monitor production metrics before widening rollout.
- Keep rollback steps documented and tested.
- Define rollback limits when new code has already written new state schema versions.
- Keep a compatibility matrix for graph version, state version, prompt version, tool version, and model version.
- For complex agents, maintain this matrix with tooling or automation; manual tracking usually becomes unreliable once multiple versions can be live at the same time.

### Testing And Evals

- Add unit tests for state reducers, tools, validators, migrations, and access checks.
- Add state-transition tests for normal, interrupted, retried, concurrent, resumed, and failed flows.
- Keep golden datasets for representative user requests, tool-routing decisions, final responses, and persisted state snapshots.
- Use regression thresholds for task success, refusal correctness, tool selection, latency, token usage, and cost.
- Use LLM-as-judge only with fixed rubrics, sampled human review, and tracked judge-model versions.
- Include adversarial cases for prompt injection, tool injection, malformed inputs, cross-tenant access, unsafe tool routing, and hidden instructions in retrieved content.
- Run tool-routing evals to check that the agent chooses the expected tool, refuses unsafe tools, and asks for approval when required.
- Test backup restore, migration rollback, duplicate tool calls, timeout handling, redaction, and resumed checkpoints from the previous production version.

---

## Operate-Time Controls

### Audit Trails For State-Changing Actions

- Record who requested the action, what changed, when it changed, which tool ran, and the before/after state summary.
- Include trace IDs, correlation IDs, tenant IDs, user IDs, thread IDs, tool-call IDs, and approval IDs where relevant.
- Make audit records append-only or tamper-evident for sensitive workflows.
- Keep audit logs separate from conversational summaries and general observability logs.

### Retries, Timeouts, Backoff, And Circuit Breakers

- Set explicit timeouts for model calls, tool calls, database calls, and external APIs.
- Use bounded retries with exponential backoff and jitter.
- Avoid retrying non-idempotent actions unless an idempotency key is enforced.
- Add circuit breakers for failing dependencies.
- Return clear recoverable errors when dependencies are unavailable.

### Graceful Degradation

- Define user-facing fallbacks for dependency failures, rate limits, quota exhaustion, model failures, and partial tool failures.
- Prefer safe partial results over silent failure when the user can still act on them.
- Queue work only when delayed execution is safe, visible to the user, and idempotent.
- Fail closed for privileged, destructive, financial, or irreversible actions.
- In this context, fail closed means rejecting the action, preserving current state, and surfacing a recoverable error or approval request. For example, if a payment tool times out after authorisation cannot be confirmed, do not retry the charge blindly; record the uncertain state and require reconciliation or human approval.
- Preserve enough state for the user or operator to resume, retry, cancel, or escalate.

### Observability: Logs, Trace IDs, Metrics, And Alerts

- Emit structured logs for requests, state transitions, tool calls, approvals, failures, retries, and degradation paths.
- Propagate trace IDs and correlation IDs across the application, model calls, tools, and external APIs.
- Track latency, error rate, retry rate, timeout rate, token usage, tool-call count, approval rate, refusal rate, degradation rate, and cost.
- Alert on failed state writes, repeated tool failures, high latency, cost spikes, unusual access patterns, and eval regressions.

### Redaction Rules For Logs And Traces

- Redact secrets, credentials, tokens, API keys, session cookies, personal data, payment data, and sensitive business data.
- Apply redaction before logs or traces leave the process.
- Keep redaction rules tested with realistic examples.
- Avoid logging full prompts, full state, full tool payloads, retrieved documents, or model outputs unless explicitly approved.

### Retention, Deletion, Backup, And Restore

- Define retention periods for state, messages, audit logs, traces, uploaded files, and generated artefacts.
- Implement deletion workflows for user and tenant data.
- Test restore from backup, not just backup creation.
- Document recovery point objective and recovery time objective.
- Ensure deletion and retention rules match legal, security, and product requirements.

### Rate Limits, Quotas, And Cost Controls

- Rate-limit by user, tenant, IP address, API key, and tool where appropriate.
- Add quotas for token usage, tool calls, external API calls, storage, and long-running threads.
- Enforce per-request and per-tenant cost ceilings.
- Degrade gracefully when limits are reached.
- Alert on unusual usage and suspected abuse.
