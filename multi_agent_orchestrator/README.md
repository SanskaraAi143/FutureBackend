# FutureBackend

FutureBackend is an AI-powered backend for orchestrating wedding planning workflows using Google ADK, Supabase, and Astra DB. It leverages modular agents for user onboarding, ritual planning, budget allocation, and vendor matching, with robust workflow management via Temporal.

## Features

- **Agent-based architecture:** Modular agents for onboarding, rituals, budget, and vendor flows
- **Supabase integration:** Stores user, vendor, and event data
- **Astra DB vector search:** Enables semantic ritual search and retrieval
- **Google ADK:** For agent development and orchestration
- **Temporal workflows:** Durable, stateful orchestration of user journeys
- **Extensible tools:** Easily add new tools and agents

## Project Structure

```
FutureBackend/
├── agent.py                # Main entry point for running the agent
├── config.py               # Configuration utilities
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .env                    # Your actual environment variables (not committed)
├── adk_agents/             # Modular agent definitions (onboarding, ritual, budget, vendor)
├── tools.py                # Tool functions for agents
├── test_connections.py     # Test DB/API connections
├── examples/               # Example agent flows and scripts
├── docs/                   # Architecture, MVP, and enhancement docs
├── utils/                  # SQL schema and utilities
└── ...
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
SUPABASE_ACCESS_TOKEN=your_supabase_access_token
ASTRA_API_TOKEN=your_astra_api_token
ASTRA_API_ENDPOINT=your_astra_api_endpoint
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

**Never commit your real `.env` file!**

## Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd FutureBackend
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.example` to `.env` and fill in all required keys as above.
5. **Test connections:**
   ```bash
   python test_connections.py
   ```

## Usage

- **Run the main agent:**
  ```bash
  python examples/run_orchestrator.py
  ```
  This will start the orchestrator agent, which manages onboarding, ritual, budget, and vendor flows.

- **Agent Structure:**
  - `adk_agents/agent.py` defines:
    - **OnboardingAgent**: Collects user details
    - **RitualSearchAgent**: Answers ritual questions
    - **BudgetAgent**: Manages budget setup
    - **VendorSearchAgent**: Finds and suggests vendors
    - **RootAgent**: Orchestrates the above agents
  - Each agent uses tools from `tools.py` and interacts with Supabase/Astra DB as needed.

- **Example flows:**
  - See `examples/` for sample scripts and flows (e.g., onboarding, vendor search, ritual search).

## Documentation

- **Architecture:** See `docs/AI_agent_architecture.md` and `docs/AI_agent_architecture_enhancements.md`
- **MVP details:** See `docs/AI_agent_architecute_MVP.md`
- **Task list:** See `docs/MVP_task_list.md`
- **Sample outputs:** See `sample_test_output.txt`

## Testing

- Use `test_connections.py` to verify DB/API connectivity.
- Write and run additional tests as needed for your agents and tools.

## License

See [LICENSE](LICENSE) for details.