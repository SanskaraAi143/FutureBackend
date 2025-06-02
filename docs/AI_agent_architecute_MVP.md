Okay, let's streamline the architecture for an initial product (MVP) focusing on your core requirements: User Onboarding & Preferences, Ritual Planning, Budget Allocation, and Vendor Matching. We'll stick to the principles of Langchain for agent logic and Temporal for stateful workflows.

The multi-modal input processing will be simplified for this initial version. We'll assume text-based interactions primarily, but the architecture will be ready to incorporate richer media processing later. The "Code Execution Agent" will be considered a "System Tool" for now, used sparingly where absolutely necessary.

---

**Initial Product: AI Agent Architecture (MVP)**

**I. Core Principles & Framework (Unchanged)**

1.  **Langchain:** For agent "brains," LLM interactions, tool usage, memory.
2.  **Temporal:** For durable, stateful, long-running workflows (e.g., `UserOnboardingWorkflow`, `InitialPlanningWorkflow`).

**II. Simplified Multi-modal Input Processing Layer (MVP)**

*   **Initial Focus:** Primarily text input.
*   **Future Hook:** The `UserInteractionAgent` will be designed to easily integrate a `ProcessUserInputActivity` (as described previously) when you're ready to handle audio/image/video. For now, if a user *mentions* an image (e.g., "I have a picture of a mandap I like"), the agent will note this preference textually.

---

**III. Core Agents & Their Tools (MVP Version)**

**A. Orchestrator Agent (The Initial Planner & Workflow Manager)**
    *   **Purpose:** Main entry point for initial planning. Decomposes high-level user goals (e.g., "Help me start planning my Hindu wedding") into onboarding, preference gathering, initial ritual understanding, budget setup, and basic vendor exploration. Triggers and manages relevant Temporal workflows.
    *   **Langchain Components:** `RouterChain`, `SequentialChain`, planning LLMs.
    *   **MVP Tools:**
        *   **Workflow Management Tool (Temporal Client):** To start, signal, query, and manage Temporal workflows like `UserOnboardingWorkflow`, `InitialRitualSetupWorkflow`, `BudgetSetupWorkflow`, `InitialVendorExplorationWorkflow`.
        *   **Agent Dispatcher Tool:** Selects and invokes other specialized agents (User Interaction, Ritual, Budget, Vendor).
        *   **State Tracking Tool (Supabase):** Logs progress of initial planning stages.
        *   **User Preferences Retrieval Tool:** Accesses `users.preferences` from Supabase.
    *   **Interaction with Temporal:** Initiates top-level Temporal workflows. The Orchestrator itself might run as part of a larger `WeddingPlanningSessionWorkflow`.

**B. User Interaction & Preferences AI Agent (The Onboarding Specialist)**
    *   **Purpose:** Handles direct chat interactions, guides the user through onboarding, collects essential information, and populates/updates the user's profile and preferences.
    *   **Langchain Components:** `ConversationChain`, `LLMChain` for summarization and preference extraction.
    *   **MVP Tools:**
        *   **Chat History Memory Tool:** (e.g., `SupabaseChatMessageHistory`)
        *   **User Profile Tool (Supabase):**
            *   `get_user_details(user_id)`: Retrieves basic user info.
            *   `update_user_preferences(user_id, updates)`: Critical for capturing culture, caste, region, initial budget ideas, number of events, guest count estimates, wedding date thoughts. This is the core of "User Preferences AI."
            *   `get_user_preferences(user_id)`
        *   **Intent Recognition Tool:** (LLM-powered) To understand user responses during onboarding.
        *   **Onboarding Questionnaire Tool:** (LLM-driven or structured prompts) Guides the user through a series of questions to gather necessary details (e.g., "What is your primary cultural background for the wedding?", "Which region's traditions will you be following primarily?", "Do you have a wedding date in mind or a preferred month?").
    *   **Interaction with Temporal:**
        *   Runs within a `UserOnboardingWorkflow` managed by Temporal. Each significant step of collecting preferences could be a Temporal activity.
        *   `UserOnboardingWorkflow` signals completion to the Orchestrator.

**C. Ritual Agent (The Cultural Foundation Layer)**
    *   **Purpose:** Provides initial information on key Hindu rituals based on the user's stated culture, caste, and region (collected by the User Interaction Agent). Generates high-level lists of common rituals.
    *   **Langchain Components:** `RetrievalQAChain` using Astra DB.
    *   **MVP Tools:**
        *   **Ritual Vector Search Tool (Astra DB):** `search_rituals(query, culture_filters)` to find common rituals matching user's background.
        *   **Basic Ritual Listing Tool:** (LLM + structured data from Astra/Supabase) Generates a list of *common* rituals for the user's context (e.g., "Based on your preferences, common rituals include Haldi, Mehendi, Sangeet, Wedding Ceremony..."). *Detailed Samagri checklists can be a V2 feature.*
        *   **Auspicious Timing Note Tool:** Reminds the user that specific timings will need to be confirmed with a Pandit.
    *   **Interaction with Temporal:**
        *   Invoked by the Orchestrator after onboarding, possibly as part of an `InitialPlanningWorkflow`.
        *   Activities like `GenerateCommonRitualListActivity`.

**D. Budget Allocation AI Agent (The Initial Financial Guide)**
    *   **Purpose:** Helps users establish a preliminary budget and suggests a high-level allocation based on their overall budget estimate, region, and number of planned events.
    *   **Langchain Components:** `LLMChain` for understanding budget input and generating allocation suggestions.
    *   **MVP Tools:**
        *   **User Preferences Tool (Supabase):** To fetch `users.preferences` (overall budget idea, number of events).
        *   **Budget Allocation Suggestion Tool:** (LLM-powered, potentially with simple heuristics/rules). Based on the total budget and number of events, suggests percentage breakdowns for major categories (e.g., "For a budget of X and Y events, typical allocations are: Venue 30-40%, Catering 25-35%, Decor 15-20%..."). *This is a suggestion, not a rigid plan.*
        *   **Budget Setup Tool (Supabase):** `create_initial_budget_categories(user_id, categories_with_allocations)`. Populates `budget_items` with category shells.
    *   **Interaction with Temporal:**
        *   Part of the `InitialPlanningWorkflow`.
        *   Activities like `SetInitialBudgetGoalActivity`, `SuggestBudgetAllocationsActivity`.

**E. Vendor Matching Agent (The Initial Connector)**
    *   **Purpose:** Performs initial searches for key vendors (e.g., Venue, Photographer, Caterer) based on user's location, initial budget per category (from Budget Agent), and stated preferences. Provides a few initial suggestions.
    *   **Langchain Components:** `RetrievalQAChain`, `LLMChain` for generating brief recommendation summaries.
    *   **MVP Tools:**
        *   **Vendor Search Tool (Supabase SQL):** `search_vendors(category, location, budget_range_for_category, keywords_from_preferences)`
        *   **User Preferences Tool (Supabase):** To get location, budget per category (e.g., `preferences.budget_allocations.venue`), and any explicitly stated style preferences.
        *   **Google Maps API Tool (Basic):** `search_nearby_places(type='wedding_venue', location=X)` for very broad initial venue discovery if Supabase yields few results.
        *   **Availability Check Tool (Supabase - Basic):** `check_vendor_availability(vendor_id, rough_date_range)`. *Detailed availability comes later.*
        *   **Portfolio Link Tool:** Provides links to vendor portfolios stored in Supabase.
    *   **Interaction with Temporal:**
        *   Invoked by the Orchestrator after initial budget and preferences are set, as part of `InitialPlanningWorkflow` or a dedicated `InitialVendorExplorationWorkflow`.
        *   Activities: `SearchInitialVenuesActivity`, `SearchInitialPhotographersActivity`.

---

**IV. Simplified End-to-End Flow (MVP)**

1.  **User Signs Up / Initiates Planning:**
    *   **Orchestrator Agent** starts `UserOnboardingWorkflow` (Temporal).
2.  **`UserOnboardingWorkflow` (Temporal):**
    *   **Activity: `CollectUserPreferencesActivity`**
        *   **User Interaction & Preferences AI Agent** engages.
        *   Uses **Onboarding Questionnaire Tool** and **User Profile Tool** to gather:
            *   Whose wedding, primary contact.
            *   Wedding date ideas (month/year).
            *   Culture, Caste, Region (critical for rituals).
            *   Estimated number of main events (e.g., Haldi, Mehendi, Wedding, Reception).
            *   Rough total budget idea (e.g., "around 10 lakhs," "15-20 lakhs").
            *   Primary location for wedding.
        *   Preferences are saved to `users` table via **User Profile Tool**.
    *   Workflow signals completion with collected preferences.
3.  **Orchestrator Agent** (reacting to `UserOnboardingWorkflow` completion) then might trigger an `InitialPlanningWorkflow` (Temporal).
4.  **`InitialPlanningWorkflow` (Temporal):**
    *   **Activity: `SetupInitialRitualsActivity`**
        *   **Ritual Agent** is invoked.
        *   Uses **Ritual Vector Search Tool** based on user's culture/caste/region.
        *   Uses **Basic Ritual Listing Tool** to provide a high-level list of common rituals.
        *   Adds a note about consulting a Pandit for specific timings.
        *   *Output:* List of common rituals stored/presented to user.
    *   **Activity: `SetupInitialBudgetActivity`**
        *   **Budget Allocation AI Agent** is invoked.
        *   Uses **User Preferences Tool** (total budget) and **Budget Allocation Suggestion Tool**.
        *   Uses **Budget Setup Tool** to create initial categories in `budget_items`.
        *   *Output:* Suggested budget breakdown presented, initial categories saved.
    *   **Activity: `ExploreInitialVendorsActivity`**
        *   **Vendor Matching Agent** is invoked.
        *   For key categories (e.g., Venue):
            *   Uses **User Preferences Tool** (location, budget for venue category).
            *   Uses **Vendor Search Tool (Supabase)**.
            *   Presents 2-3 initial vendor suggestions with portfolio links.
        *   *Output:* A few initial vendor names/links.
5.  **Interaction Continues:** The user can then ask more specific questions, which would refine preferences or trigger more detailed searches, gradually moving towards more advanced features in later product versions.

**Key Simplifications for MVP:**

*   **No advanced multi-modal processing:** Text is primary.
*   **Ritual agent is informational:** Provides lists, not deep samagri or specific auspicious timings (defers to Pandit).
*   **Budget agent provides suggestions:** Not detailed tracking or expense input yet.
*   **Vendor agent provides initial exploration:** Not detailed booking, contract management, or complex negotiation.
*   **No image/video generation.**
*   **No proactive "Failure Point Detection Agent" yet.** Emergency handling (like Pandit unavailability) will be a manual process or a very simple notification in V1.
*   **"Task Decomposition Agent" is implicitly part of the Orchestrator's logic** for this simpler flow.
*   **"Plan Optimization Agent" and "Full Plan Creation Agent" are for later versions.** MVP focuses on getting the foundational pieces in place.
*   **WhatsApp API and advanced communication are deferred.** Initial comms are in-app.
*   **Code Execution Tool** is used minimally, if at all, for very specific, pre-defined logic that can't be easily done with LLMs or SQL.

This MVP architecture sets the stage. Each agent and workflow can be enhanced iteratively, adding more tools, more sophisticated logic, and richer multi-modal capabilities as the product evolves. The use of Temporal ensures that even these initial workflows are robust and can be expanded without losing state or context.