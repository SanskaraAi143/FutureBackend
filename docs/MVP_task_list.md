# MVP Implementation Task List (Supabase + Astra DB, Google ADK)

This checklist is tailored for building the MVP using the Google Agent Development Kit (ADK), Supabase (for all user/vendor/event data), and Astra DB (for ritual vector search). The orchestration now uses a single LlmAgent as the root orchestrator, with specialized LlmAgent sub-agents for onboarding, ritual, budget, and vendor flows. The flow is strictly: onboarding (user details), then vendor preferences, then budget allocation, with the orchestrator handling out-of-order or extra queries as described in the MVP.

---

## 1. Project Setup
- [x] **Initialize Python project & environment** (Complexity: Low)
    - [x] Set up virtualenv/conda
    - [x] Install Google ADK, Supabase Python client, Astra DB client, and dependencies
    - [x] Set up code structure (folders, main files)
    - [x] Configure Google Cloud, Supabase, and Astra DB credentials

---

## 2. Database Integration
- [x] **Connect to Supabase using overall_schema.sql** (Complexity: High)
    - [x] Set up Supabase instance with provided schema
    - [x] Integrate Supabase Python client for all CRUD operations (users, vendors, etc.)
    - [x] Implement data validation and permissions

---

## 3. Ritual Vector Search Integration
- [x] **Connect to Astra DB for ritual search** (Complexity: Medium)
    - [x] Set up Astra DB keyspace and vector table for rituals
    - [x] Integrate Astra DB Python client
    - [x] Implement search and retrieval logic for rituals

---

## 4. Core Agent & Tool Design (ADK)
- [ ] **Define agent pipeline using ADK** (Complexity: High)
    - [ ] Use a single LlmAgent as the root orchestrator (no SequentialAgent)
    - [ ] Implement LlmAgent sub-agents for onboarding, ritual, budget, and vendor flows
    - [ ] Use ADK session state for data passing between agents
    - [ ] Write detailed, flow-enforcing prompts for each agent (see MVP: onboarding first, then vendor, then budget, orchestrator handles out-of-order queries)
- [ ] **Integrate Supabase and Astra DB tools/APIs** (Complexity: High)
    - [x] Use FunctionTool or built-in ADK tools for Supabase data fetch, search, and updates
    - [x] Register Astra DB search as a tool for ritual queries
    - [ ] Implement error handling and retries for all tool calls

---

## 5. Workflow Orchestration
- [ ] **Implement main workflow agent** (Complexity: High)
    - [ ] Compose LlmAgent as the orchestrator for the full user journey (onboarding → vendor → budget → ritual)
    - [ ] Ensure state is shared and updated across all steps
    - [ ] Add conditional logic for edge cases (e.g., missing data, user clarification needed, out-of-order queries)

---

## 6. Error Handling & Human Escalation
- [ ] **Implement robust error handling** (Complexity: Medium)
    - [ ] Validate all user and agent inputs
    - [ ] Handle API/data errors with user-friendly messages
    - [ ] Add human-in-the-loop escalation for unresolved or ambiguous cases (see ADK FunctionTool pattern)

---

## 7. Testing & Evaluation
- [ ] **Write agent evaluation tests** (Complexity: Medium)
    - [ ] Use ADK's agent evaluation framework and `.test.json` files
    - [ ] Test with real data and user scenarios
    - [ ] Validate agent outputs and state transitions

---

## 8. Documentation & Deployment
- [ ] **Document setup and usage** (Complexity: Low)
    - [ ] README with setup, credentials, and usage instructions
    - [ ] Example user flows and agent pipeline diagrams
- [ ] **Prepare for deployment** (Complexity: Medium)
    - [ ] Set up deployment scripts (Cloud Run, GKE, or VM)
    - [ ] Secure credentials and environment variables

---

## 9. Review & Iteration
- [ ] **Review MVP with stakeholders** (Complexity: Low)
    - [ ] Collect feedback
    - [ ] Prioritize next steps

---

> _Check off each task as you complete it. This list is designed for a real-data, production-oriented MVP using Google ADK, Supabase, and Astra DB. Use ADK Web for agent testing and omit custom UI for now._
