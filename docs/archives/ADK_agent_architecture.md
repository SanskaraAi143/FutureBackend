# Sanskara AI – Google ADK Agent System Architecture (Supabase + Astra DB)

## 1. Overview
This architecture describes the production-ready, modular agent system for Sanskara AI, built using Google ADK, Supabase, and Astra DB. It reflects the actual implementation in the codebase (`agent.py`, `tools.py`, etc.) and aligns with the ADK implementation plan.

## 2. Agent Pipeline & Orchestration

### 2.1 Root Orchestrator Agent (`RootAgent`)
- **Type:** `LlmAgent`
- **Role:** Single entry point for all user interactions after onboarding. Delegates tasks to sub-agents, manages session state, handles out-of-order queries, and ensures robust, user-friendly responses.
- **Sub-agents:**
  - `OnboardingAgent`: Collects user details and preferences.
  - `RitualSearchAgent`: Answers ritual/cultural questions using Astra DB.
  - `BudgetAgent`: Manages budget setup and suggestions using Supabase.
  - `VendorSearchAgent`: Finds and suggests vendors using Supabase.
- **Session State:** Uses `InvocationContext.session.state` to pass data/results between agents. Each agent reads/writes only its relevant keys.
- **Callbacks:** (Planned) before/after tool/model callbacks for guardrails, logging, and self-healing.
- **Error Handling:** All tool calls and LLM invocations are wrapped with async retry logic. Escalates to human if repeated failures occur.

### 2.2 Sub-Agents
- **OnboardingAgent:**
  - Tools: `get_user_id`, `get_user_data`, `update_user_data` (Supabase via MCP)
  - Prompts enforce minimal, efficient data collection and confirmation.
- **RitualSearchAgent:**
  - Tools: `search_rituals` (Astra DB vector search)
  - Provides culturally accurate ritual info, defers to Pandit for specifics.
- **BudgetAgent:**
  - Tools: `add_budget_item`, `get_budget_items`, `update_budget_item`, `delete_budget_item` (Supabase)
  - Suggests budget breakdowns, validates all inputs, confirms with user.
- **VendorSearchAgent:**
  - Tools: `list_vendors`, `get_vendor_details` (Supabase)
  - Finds vendors by category/location, provides details and portfolio links.

## 3. Tooling & Integration
- All tools are async, robust, and defined in `tools.py`.
- Supabase and Astra DB access is via MCPToolset (see `examples/tmp.py`).
- Tools are registered with the correct agents and signatures match ADK requirements.
- Retry and error handling is implemented for all tool calls.

## 4. Session State & Data Passing
- All data passing between agents is via ADK session state (`InvocationContext.session.state`).
- Each agent writes its output to a unique key for downstream agents.
- Orchestrator manages state transitions and ensures data consistency.

## 5. Error Handling, Guardrails, and Self-Healing
- All tool/model calls are wrapped with an async retry decorator (see `agent.py`).
- Planned: before/after tool/model callbacks for guardrails (input validation, quota checks), logging, and artifact saving.
- On repeated failures, the orchestrator escalates to a human operator.

## 6. Edge Case Handling
- Orchestrator detects and recovers from stuck/looping flows, missing/ambiguous/conflicting data, and invalid inputs.
- All agents validate inputs and outputs, ask clarifying questions, and save critical state for recovery.
- Human-in-the-loop escalation is supported for unresolved cases.

## 7. Testing & Evaluation
- Test coverage for all major agents and tools (`test_agent_subagents.py`).
- `.test.json` evaluation files (planned) for all major flows and edge/error cases.
- Automated tests validate agent outputs, state transitions, and error handling.

## 8. Deployment & Monitoring
- Deployment scripts (planned) for Cloud Run, GKE, or VM.
- Logging, monitoring, and alerting for all agent/tool/LLM failures and escalations (planned).
- All credentials and environment variables are securely managed.

## 9. Extensibility
- New agents/tools can be added by defining them in `agent.py`/`tools.py` and registering with the orchestrator.
- The architecture supports future enhancements: multi-modal input, advanced scheduling, communication agents, etc.

---

This document supersedes previous architecture drafts and is referenced in the ADK implementation plan. It is kept up-to-date with the actual codebase and best practices from the latest ADK documentation.
