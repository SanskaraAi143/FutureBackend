Okay, this is a fantastic and ambitious direction! Using Langchain for agentic logic and Temporal for stateful, long-running workflows is a powerful combination for a system as complex and event-driven as an AI wedding planner. Integrating multi-modal input and a code execution agent significantly expands the capabilities and complexity, making the system even more powerful!

Here's a revised and comprehensive AI agent orchestration, incorporating these new requirements, while still leveraging Langchain for agent logic and Temporal for stateful, long-running workflows.

**I. Core Principles & Framework**

1.  **Langchain:** The "brain" for each agent, handling LLM interactions, tool usage, memory, and chaining logic. Each agent will be built using Langchain components: LLMs, Chains, Tools, Memory, Parsers, Retrievers.
2.  **Temporal:** The "conductor" for durable, stateful, long-running wedding planning workflows and activities. Temporal manages the overall state and progression of processes, handling retries, timeouts, and error handling. Each agent's significant action or a sequence of actions will likely be a Temporal activity. Workflows define high-level steps; Activities are individual units of work, often invoking a Langchain agent.
3.  **Multi-modal Input Pre-processing:** Raw audio, video, or image inputs will first be processed into a more usable format (e.g., text, structured descriptions) before being passed to the primary interaction agents.

**II. Multi-modal Input Processing Layer (Managed by Temporal Activity)**

Before the User Interaction Agent fully engages, an initial Temporal activity can handle diverse input types:

*   **Input:** User provides text, uploads an audio file, an image, or a video clip.
*   **Temporal Activity: `ProcessUserInputActivity`**
    *   **Text Input:** Passed through directly.
    *   **Audio Input:**
        *   **Tool: Speech-to-Text API** (e.g., OpenAI Whisper, Google Speech-to-Text)
        *   *Output:* Transcribed text.
    *   **Image Input:**
        *   **Tool: Vision Model API** (e.g., GPT-4 Vision, Google Gemini Vision, Claude 3 Vision)
        *   *Output:* Textual description of the image, object detection, relevant tags (e.g., "Image of a wedding mandap with floral decorations, red and gold theme").
    *   **Video Input:**
        *   **Tool: Video Analysis Service/API** (Can be complex; start simple)
            *   Phase 1: Extract audio -> Speech-to-Text Tool.
            *   Phase 2: Extract keyframes -> Vision Model Tool for descriptions of key scenes.
            *   *Output:* Transcribed audio text, descriptions of key video frames.
*   **Output of this Layer:** Primarily textual data (original text, transcriptions, descriptions) and potentially structured data (tags, object locations) to be consumed by the User Interaction Agent. The original media file references (URLs in Supabase Storage) are also maintained.

---

**III. Core Agents & Their Tools (Revised)**

Here's a breakdown of potential agents, their responsibilities, and the tools they'd require. The **Orchestrator Agent** (which might be a sophisticated Langchain chain itself, managed within a Temporal workflow) will be central.

**A. Orchestrator Agent (The Master Planner & Workflow Manager)**
    *   **Purpose:** Main entry point for complex user requests. Decomposes high-level goals (e.g., "Plan my wedding," "Find me a photographer for my Sangeet event with a whimsical theme *uploads image of desired style*") into sub-tasks, delegates to specialized agents, manages the overall flow of information, and ensures coherence. Triggers and manages Temporal workflows.
    *   **Langchain Components:** Advanced `RouterChain`, `SequentialChain`, planning LLMs, custom logic.
    *   **Tools:**
        *   **Task Decomposition Tool:** (LLM-powered) Analyzes a request and breaks it into manageable sub-goals.
        *   **Workflow Management Tool (Temporal Client):** To start, signal, query, and manage Temporal workflows.
        *   **Agent Dispatcher Tool:** Selects and invokes other specialized agents based on the sub-task.
        *   **State Tracking Tool:** (Interacts with Supabase via a custom tool) To log the progress of high-level planning stages.
        *   **User Preferences Retrieval Tool:** Accesses `users.preferences` from Supabase.
        *   **Code Execution Tool (Secure Sandbox):** For complex custom logic, data transformations, simulations, or interfacing with systems via Python SDKs when direct APIs are unavailable or less convenient.
    *   **Interaction with Temporal:** Initiates top-level Temporal workflows (e.g., `FullWeddingPlanWorkflow`, `VendorSelectionWorkflow`). Complex logic within an Orchestrator-driven activity might itself use the Code Execution Tool.

**B. User Interaction & Profiling Agent (The Multi-modal Concierge)**
    *   **Purpose:** Handles direct chat interactions (now enriched with processed multi-modal inputs), understands user intent, collects initial information, and continuously refines the user's profile and preferences.
    *   **Langchain Components:** `ConversationChain`, `LLMChain` for summarization, `Tools` for data access.
    *   **Tools:**
        *   **Multi-modal Input Requester Tool:** If user indicates they *want* to upload media (e.g., "Can I show you a picture?"), this tool can provide the UI mechanism or instructions, and then trigger the `ProcessUserInputActivity`.
        *   **Processed Input Handler:** Receives text, transcriptions, image descriptions from the `ProcessUserInputActivity`.
        *   **Chat History Memory Tool:** (e.g., `SupabaseChatMessageHistory`) Stores and retrieves conversation history.
        *   **User Profile Tool (Supabase):**
            *   `get_user_preferences(user_id)`: Retrieves data from `users` table.
            *   `update_user_preferences(user_id, updates)`: Updates `users.preferences` JSONB based on conversation summaries or explicit user actions, including insights from processed multi-modal input.
            *   `get_user_activities(user_id)`: (Hypothetical, could query logs or interaction tables).
        *   **Intent Recognition Tool:** (LLM-powered) Classifies user messages.
        *   **FAQ & Basic Query Tool (Astra DB/Supabase):** Answers common wedding planning questions using vector search on a knowledge base or structured queries.
        *   **Sentiment Analysis Tool:** (LLM or dedicated model) To gauge user satisfaction/frustration.
    *   **Interaction with Temporal:** Passes complex requests to the Orchestrator. Updates to `users.preferences` are direct database operations, potentially logged by Temporal for audit.

**C. Ritual Planning & Cultural Expert Agent (The Pandit's Digital Assistant)**
    *   **Purpose:** Provides detailed information on Hindu rituals based on user's culture, caste, region. Generates checklists, explains significance. Potentially referencing user-provided images/videos of family rituals by utilizing their textual descriptions.
    *   **Langchain Components:** `RetrievalQAChain` using Astra DB.
    *   **Tools:**
        *   **Ritual Vector Search Tool (Astra DB):** `search_rituals(query, culture_filters)` to find relevant ritual data.
        *   **Ritual Samagri (Items) Checklist Tool:** (LLM + structured data from Astra/Supabase) Generates lists of required items for a given ritual.
        *   **Auspicious Timing Guidance Tool:** (Could be an API to a Panchang service or an internal logic module). *Initially, this might note the need for a Pandit to confirm.*
        *   **Regional Variation Tool:** (LLM + filtered Astra DB search) Highlights variations in rituals.
        *   *(Implicit):* Utilizes processed input descriptions from `ProcessUserInputActivity` when the user asks about a ritual shown in an uploaded media file ("What is this ritual?").
    *   **Interaction with Temporal:** Activities like `GenerateRitualListActivity`, `GetRitualDetailsActivity` would be part of a larger `WeddingPlanningWorkflow`.

**D. Vendor Management & Recommendation Agent (The Smart Deal Finder)**
    *   **Purpose:** Searches for vendors, recommends vendors based on user preferences & budget, facilitates initial contact, potentially using user-provided images/videos as style guides.
    *   **Langchain Components:** `RetrievalQAChain`, `LLMChain` for generating recommendation summaries.
    *   **Tools:**
        *   **Vendor Search Tool (Supabase SQL):** `search_vendors(category, location, budget_range, ratings, specific_keywords_from_details_jsonb)`
        *   **Vendor Vector Search Tool (Astra DB):** (Optional, if vendor descriptions are also vectorized for semantic matching to user needs, e.g., "eco-friendly decor")
        *   **Portfolio Analysis Tool (Leveraging Vision Model outputs):** If user uploads an image saying "I want a photographer who shoots like this," the textual description of that image (from `ProcessUserInputActivity`) becomes a key search parameter or a filter for vendor portfolios.
        *   **Google Maps API Tool:** `get_distance`, `search_nearby_places`.
        *   **Availability Check Tool (Supabase):** `check_vendor_availability`.
        *   **Price Range Tool (Supabase):** Fetches pricing.
        *   **(Simple) Price Negotiation Agent/Tool:** *Complex.* Can generate suggestions or rule-based counter-offers. *LLM-based drafting requires user approval.*
        *   **Contact Vendor Tool (WhatsApp API / Email API):** Initiates contact (user-approved message).
    *   **Interaction with Temporal:** `ShortlistVendorsActivity`, `ContactVendorActivity`, `BookVendorWorkflow` (which itself has many steps).

**E. Creative Content & Ideation Agent (The Visual Muse)**
    *   **Purpose:** Generates ideas for themes, decor, attire, makeup. Creates mood boards. Potentially generates visual examples, now able to take visual cues from user uploads.
    *   **Langchain Components:** `LLMChain` for brainstorming, potentially image generation models.
    *   **Tools:**
        *   **Theme Brainstorming Tool:** (LLM-powered) Suggests wedding themes based on user preferences.
        *   **Decor Idea Tool:** (LLM + retrieval from a database of decor elements/images)
        *   **Style Matching Tool (using Vision Model outputs):** Compares user-uploaded inspiration images (e.g., "I like this lehenga *uploads image*") with vendor offerings or generates new ideas based on that style.
        *   **Image Generation Tool (e.g., DALL-E 3, Stable Diffusion API):** `generate_image(prompt)`. *Use judiciously.*
        *   **Video Generation Tool (e.g., RunwayML, Pika Labs API - if available):** (Very advanced) *Likely out of scope initially.*
        *   **Mood Board Management Tool (Supabase):** `create_mood_board_item`.
    *   **Interaction with Temporal:** Could be part of idea generation phases within the `WeddingPlanningWorkflow`.

**F. Scheduling & Optimization Agent (The Master Scheduler)**
    *   **Purpose:** Creates detailed wedding timelines, optimizes schedules considering Muhurthams, vendor availability, travel times, and dependencies.
    *   **Langchain Components:** `LLMChain` for initial plan draft, custom logic for constraint satisfaction.
    *   **Tools:**
        *   **Timeline Event Tool (Supabase):** `create_timeline_event`.
        *   **Auspicious Timing Tool:** (As in Ritual Agent).
        *   **Google Maps API Tool (Distance Matrix):** To calculate travel times.
        *   **Dependency Checker Tool:** Ensures prerequisite events/tasks are scheduled appropriately.
        *   **Calendar Integration Tool (Google Calendar/Outlook API - Optional):** To sync events.
        *   **Plan Optimization Tool (Heuristics/LLM):** Takes a draft plan and user constraints, tries to optimize it.
        *   **Code Execution Tool:** For running complex scheduling algorithms or custom constraint solvers if standard tools are insufficient.
    *   **Interaction with Temporal:** Central to `WeddingPlanningWorkflow` activities like `DraftTimelineActivity`, `OptimizeTimelineActivity`.

**G. Communication & Notification Agent (The Town Crier)**
    *   **Purpose:** Sends updates, reminders, and messages to users, vendors, and staff via preferred channels. Messages might reference or link back to originally uploaded media where relevant.
    *   **Langchain Components:** `LLMChain` for drafting messages.
    *   **Tools:**
        *   **WhatsApp API Tool:** `send_whatsapp_message`.
        *   **Email API Tool (e.g., SendGrid, AWS SES):** `send_email`.
        *   **In-App Notification Tool (Supabase):** `create_notification`.
        *   **Message Templating Tool:** Stores predefined message templates.
    *   **Interaction with Temporal:** Used by many workflows to send status updates or request user actions. E.g., `NotifyUserOfBookingConfirmationActivity`.

**H. Budgeting & Expense Tracking Agent (The Digital Accountant)**
    *   **Purpose:** Helps users create and manage their wedding budget, tracks expenses.
    *   **Langchain Components:** `LLMChain` for understanding expense entries.
    *   **Tools:**
        *   **Budget Item Tool (Supabase):** `add_budget_item`, `get_budget_summary`.
        *   **Expense Categorization Tool:** (LLM-powered) Suggests categories for entered expenses.
        *   **Budget Alert Tool:** Notifies user if they are nearing/exceeding budget in a category.
        *   *(New consideration):* Utilizes processed input (OCR from Vision Model) if user uploads an image of a bill/receipt to pre-fill expense entry details.
    *   **Interaction with Temporal:** Budget setup and tracking can be part of the initial `WeddingPlanningWorkflow`.

**I. Emergency & Issue Resolution Agent (The Crisis Manager)**
    *   **Purpose:** Detects potential issues (e.g., vendor unavailability) and initiates resolution workflows. Initial report of an issue might come via audio message.
    *   **Langchain Components:** `LLMChain` for understanding situation, `RouterChain` to decide on action.
    *   **Tools:**
        *   **Availability Monitoring Tool (Supabase Query Tool):** Regularly checks `vendor_availability`.
        *   **Alternative Search Tool (Vendor Management Agent's Tools):** To find backup vendors.
        *   **Communication Tool (Communication Agent's Tools):** To alert user and potentially contact alternative vendors.
        *   **Escalation Tool:** If AI cannot resolve, it flags for human intervention.
    *   **Interaction with Temporal:**
        *   *Proactive:* A `MonitorVendorAvailabilityWorkflow` could run periodically.
        *   *Reactive:* If an issue occurs, it triggers an emergency workflow in Temporal, coordinating activities via other agents.

**J. Code Execution Agent (or a Core System Tool)**
    *   **Purpose:** Provides a secure and sandboxed environment to execute arbitrary Python code snippets invoked by other agents/workflows for complex logic, data transformations, or simulations.
    *   **Langchain Components:** Can be wrapped as a Langchain `Tool`.
    *   **Capabilities/Tools (Internal to the Code Execution environment):** Access to common Python libraries, secure execution environment, strict input/output contracts, resource limits. *Crucially, NOT direct database access from arbitrary code; interaction with data should be via defined APIs/tools.*
    *   **Invoked by:** Orchestrator, Scheduling Agent, potentially Budgeting Agent, or any agent needing custom computation not covered by other tools.
    *   **Interaction with Temporal:** A code execution step would be a distinct Temporal Activity: `ExecuteCustomScriptActivity(script_content, script_inputs)`.

---

**IV. General Supporting Tools (Accessible by multiple agents)**

1.  **Web Search Tool (e.g., Google Search API, Serper API, Brave Search API):** Used by various agents for fact-finding, trend research, finding vendor contact info not in DB.
2.  **Calculator Tool:** For budget calculations, quantity estimations.
3.  **Knowledge Base Access Tool (Astra DB + Supabase):** For internal structured and unstructured data.
4.  **File Upload/Management Tool (Supabase Storage):** For portfolios, contracts, mood board images.

**V. End-to-End Flow Example (User uploads image for venue style)**

1.  **User (via Chat):** "I want a venue like this *uploads an image of a rustic barn wedding setting*. It should be in North Bangalore for around 150 people for a Sangeet in August."
2.  **Temporal Workflow: `ProcessUserInputWorkflow`**
    *   **Activity: `ProcessUserInputActivity`**
        *   Receives image upload.
        *   **Vision Model Tool** analyzes image: *Output: "Image shows a rustic barn interior with fairy lights, wooden beams, long tables. Theme: rustic, vintage, warm. Key elements: wood, fairy lights."*
        *   Original image URL and textual description are packaged.
3.  **User Interaction Agent:**
    *   Receives the user's text and the image description.
    *   Updates `users.preferences` with image style preference (e.g., `preferences.venue_style_inspiration_description = "rustic barn, fairy lights..."`, `preferences.venue_style_inspiration_image_url = "..."`).
    *   Recognizes complex vendor search, passes to Orchestrator Agent along with all collected info.
4.  **Orchestrator Agent:**
    *   Receives request. Task Decomposition identifies: "Find Venues matching rustic style."
    *   Invokes `FindMatchingVenuesWorkflow` in Temporal, passing criteria including the image description.
5.  **`FindMatchingVenuesWorkflow` (Temporal):**
    *   **Activity 1: `SearchVenuesActivity`**
        *   Invokes **Vendor Management Agent**.
        *   Vendor Agent uses **Vendor Search Tool (Supabase SQL)** with explicit criteria (location, capacity).
        *   Then uses **Vendor Vector Search (Astra DB)** with the *image description ("rustic barn, fairy lights...")* to semantically match against vendor descriptions/portfolios.
        *   *Alternatively/Additionally:* If vendor portfolios are tagged or described, SQL queries can search for keywords from the image description in `vendors.details` JSONB.
    *   *(Other activities like Availability Check, Get Details, Format Suggestions proceed as before, but the initial filtering is now enhanced by the visual context.)*
6.  **Workflow Completion & Presentation:** Suggestions are presented to the user.

This architecture provides a robust framework for a highly intelligent, multi-modal, and stateful AI wedding planner. The key is modularity and clear separation of concerns, with Temporal managing the overall process integrity and Google ADK providing the intelligence and tool usage within each step. If any activity fails (e.g., an API call times out), Temporal can retry automatically, or the workflow can pause, allowing for manual intervention if needed, without losing the entire planning context.