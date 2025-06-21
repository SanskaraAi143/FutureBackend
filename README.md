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
├── main.py                 # Main entry point for the application
├── config/                 # Configuration files
│   ├── settings.py         # Loads environment variables
│   └── __init__.py
├── src/                    # Source code
│   ├── agents/             # ADK agent definitions
│   │   ├── orchestrator_agent.py
│   │   ├── onboarding_agent.py
│   │   └── ...             # Other agents
│   ├── tools/              # Tools for agents, organized by domain
│   │   ├── user_tools.py
│   │   └── ...             # Other tool modules
│   ├── services/           # Services for interacting with external systems (DBs, APIs)
│   │   ├── supabase_service.py
│   │   ├── astradb_service.py
│   │   └── adk_service.py
│   ├── core/               # Core business logic or schemas
│   │   └── schemas.py
│   └── __init__.py
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .env                    # Your actual environment variables (not committed)
├── tests/                  # Unit and integration tests
│   ├── unit/
│   └── integration/
├── examples/               # Example agent flows and scripts
├── docs/                   # Project documentation
└── .gitignore
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your credentials. The following variables are essential:

-   `GOOGLE_API_KEY`: Your Google API Key (for Gemini, etc.).
-   `SUPABASE_URL`: Your Supabase project URL.
-   `SUPABASE_KEY`: Your Supabase project public API key (anon key).
-   `SUPABASE_ACCESS_TOKEN`: Your Supabase service role key or a dedicated access token for server-side operations (used by MCP).
-   `SUPABASE_PROJECT_ID`: Your Supabase project ID (found in your Supabase project settings, required for MCP).
-   `ASTRA_API_TOKEN`: Your Astra DB Application Token.
-   `ASTRA_API_ENDPOINT`: Your Astra DB API Endpoint.

Optional variables (see `.env.example` for more and defaults in `config/settings.py`):

-   `TAVILY_API_KEY`: For Tavily search integration, if used.
-   `ASTRA_DB_ID`: Your Astra database ID.
-   `ASTRA_DB_REGION`: The region of your Astra database.
-   `APP_NAME`: Application name override.
-   `DEFAULT_LLM_MODEL`: Override the default LLM model.

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

- **Run the application:**
  ```bash
  python main.py
  ```
  This will start the main application, which will initialize and run the orchestrator agent (RootAgent) responsible for managing the various planning flows.

- **Agent Structure (under `src/agents/`):**
  - `orchestrator_agent.py` (or similar, e.g., `root_agent.py`) will define the main **RootAgent**.
  - Other files like `onboarding_agent.py`, `ritual_agent.py`, `budget_agent.py`, `vendor_search_agent.py` will define the respective sub-agents.
  - Each agent utilizes tools defined in `src/tools/` (e.g., `user_tools.py`, `budget_tools.py`) which in turn use services from `src/services/` to interact with Supabase, Astra DB, etc.

- **Example flows:**
  - See `examples/` for sample scripts and flows. These will be updated to reflect the new structure and usage patterns.

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