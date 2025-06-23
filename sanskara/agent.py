# agents.py - ADK agents for the Sanskara AI application
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv
import os

from google.adk.agents import Agent, SequentialAgent, LlmAgent, Agent
from google.adk.events import Event, EventActions
from google.adk.models import LlmRequest,LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, List, Dict, Any, Optional, Callable
from opik.integrations.adk import OpikTracer
from google.adk.planners import PlanReActPlanner
opik_tracer = OpikTracer()
from google.adk.sessions import InMemorySessionService
from google.adk.memory import BaseMemoryService,InMemoryMemoryService

from sanskara.tools import (
    get_user_id,
    get_user_data,
    update_user_data,
    list_vendors,
    get_vendor_details,
    add_budget_item,
    get_budget_items,
    update_budget_item,
    delete_budget_item,
    search_rituals
)
import logging
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Sub-Agents ---

ONBOARDING_PROMPT = (
    """You are the Onboarding Agent for Sanskara AI.
    You are provided with the user's email address. Your job is to:
    1. Get the user ID using the email address.
    2. Get the user data using the user ID.
    3. Collect and confirm all required user details for wedding planning in as few steps as possible.
    When requesting information, always ask for multiple related fields together (e.g., name, email, wedding date, culture, region, etc.) to minimize back-and-forth.
    If any information is already available in session.state, use it to pre-fill or skip questions.
    IMPORTANT: Only write to the following top-level fields in the users table: display_name, wedding_date, wedding_location, wedding_tradition, user_type. All other user attributes (such as caste, culture, region, budget, guest count, etc.) MUST be stored inside the preferences dictionary. Do NOT attempt to write any other fields at the top level.
    You must collect: full name, email, wedding date (or preferred month/year), culture, caste, region, estimated budget, guest count, and location.
    If the user's name is available in the session.state, greet them by name.
    If the user's email is available in the session.state, ask them to confirm it.
    If above information is already available, show it to the user and transfer control to the orchestrator agent.
    When onboarding is complete, update session.state with the user's name, email, wedding date, culture, caste, region, estimated budget, guest count, and location, confirm all collected details, and transfer control back to the Orchestrator."""
)

onboarding_agent = LlmAgent(
    name="OnboardingAgent",
    model="gemini-1.5-flash",
    description="Handles user onboarding.",
    instruction=ONBOARDING_PROMPT,
    tools=[get_user_id, get_user_data, update_user_data],
    output_key="onboarding_state",
)

RITUAL_PROMPT = (
    "You are the Ritual Agent for Sanskara AI."
    "You are a professional expert in Hindu wedding rituals, and your role is to provide accurate and culturally relevant information about these rituals."
    "When called, check session.state for the user's culture, caste, and region, and use this information to tailor your responses. If this information is not available in session.state, use your tools to retrieve it."
    "Your job is to provide clear, concise, and culturally accurate information about Hindu wedding rituals, based strictly on the user's culture, caste, and region."
    "List the most relevant rituals, explain their significance, and answer questions about them."
    "If asked for samagri (items) or specific timings, explain that a Pandit should be consulted for exact details. "
    "Use your tools to search for rituals in the database. "
    "Never answer questions outside of rituals. If asked, you must redirect to the relevant agent. "
    "All data access is performed using robust, async tools for reliability. "
    "Before using tools, check session.state for existing values."
    "After completing the ritual search, update session.state with only details which capture user needs."
    "Always format your answers for clarity and completeness."
)

ritual_search_agent = LlmAgent(
    name="RitualSearchAgent",
    model="gemini-1.5-flash",
    description="Handles ritual search.",
    instruction=RITUAL_PROMPT,
    tools=[search_rituals],
<<<<<<< HEAD
    output_key="ritual_search_state",
    
)

# --- Sub-Agents ---

ONBOARDING_PROMPT = (
    """You are the Onboarding Agent for Sanskara AI.
    You are provided with the user's email address. Your job is to:
    1. Get the user ID using the email address.
    2. Get the user data using the user ID.
    3. Collect and confirm all required user details for wedding planning in as few steps as possible.
    When requesting information, always ask for multiple related fields together (e.g., name, email, wedding date, culture, region, etc.) to minimize back-and-forth.
    If any information is already available in session.state, use it to pre-fill or skip questions.
    IMPORTANT: Only write to the following top-level fields in the users table: display_name, wedding_date, wedding_location, wedding_tradition, user_type. All other user attributes (such as caste, culture, region, budget, guest count, etc.) MUST be stored inside the preferences dictionary. Do NOT attempt to write any other fields at the top level.
    You must collect: full name, email, wedding date (or preferred month/year), culture, caste, region, estimated budget, guest count, and location.
    If the user's name is available in the session.state, greet them by name.
    If the user's email is available in the session.state, ask them to confirm it.
    If above information is already available, show it to the user and transfer control to the orchestrator agent.
    When onboarding is complete, update session.state with the user's name, email, wedding date, culture, caste, region, estimated budget, guest count, and location, confirm all collected details, and transfer control back to the Orchestrator."""
)

onboarding_agent = LlmAgent(
    name="OnboardingAgent",
    model="gemini-1.5-flash",
    description="Handles user onboarding.",
    instruction=ONBOARDING_PROMPT,
    tools=[get_user_id, get_user_data, update_user_data],
    output_key="onboarding_state",
)

RITUAL_PROMPT = (
    "You are the Ritual Agent for Sanskara AI."
    "You are a professional expert in Hindu wedding rituals, and your role is to provide accurate and culturally relevant information about these rituals."
    "When called, check session.state for the user's culture, caste, and region, and use this information to tailor your responses. If this information is not available in session.state, use your tools to retrieve it."
    "Your job is to provide clear, concise, and culturally accurate information about Hindu wedding rituals, based strictly on the user's culture, caste, and region."
    "List the most relevant rituals, explain their significance, and answer questions about them."
    "If asked for samagri (items) or specific timings, explain that a Pandit should be consulted for exact details. "
    "Use your tools to search for rituals in the database. "
    "Never answer questions outside of rituals. If asked, you must redirect to the relevant agent. "
    "All data access is performed using robust, async tools for reliability. "
    "Before using tools, check session.state for existing values."
    "After completing the ritual search, update session.state with only details which capture user needs."
    "Always format your answers for clarity and completeness."
)

ritual_search_agent = LlmAgent(
    name="RitualSearchAgent",
    model="gemini-1.5-flash",
    description="Handles ritual search.",
    instruction=RITUAL_PROMPT,
    tools=[search_rituals],
    output_key="ritual_search_state",
=======
    before_agent_callback=opik_tracer.before_agent_callback,
    after_agent_callback=opik_tracer.after_agent_callback,
    before_model_callback=opik_tracer.before_model_callback,
    after_model_callback=opik_tracer.after_model_callback,
    before_tool_callback=opik_tracer.before_tool_callback,
    after_tool_callback=opik_tracer.after_tool_callback,
>>>>>>> parent of 6547be4 (Refactor: Integrate DatabaseSessionService and improve DB handling)
)

BUDGET_PROMPT = (
    "You are the Budget Agent for Sanskara AI. "
    "When invoked, always first check session.state for the user's preferences, region. and get existing budget items using tool. If this information is not available in session.state, fetch it from the users and budget_items tables."
    "Only ask the user for information if it is missing or unclear in session.state or the database."
    "If the user wants to plan a budget, first retrieve the total budget amount and a list of budget categories from session.state. If this information is not available in session.state, retrieve any existing budget list, preferences, and location from the user's profile, and use these to provide a detailed, personalized budget breakdown."
    "Present a clear, itemized budget suggestion using all available user data. "
    "If any required information is missing, ask for it in as few steps as possible. "
    "Don't ask any data related to database data that should be handled internally, first ask orchestrator agent to fetch the data. "
    "All budget operations are performed using robust, async tools that interact with Supabase via the MCP server, ensuring reliability and up-to-date information."
    "Always check for errors in tool output and if any input is invalid, respond with a clear error message such as 'Error: Invalid input ...' or 'Error: ...'."
    "Before using tools, check session.state for existing values."
    "After completing the budget setup, update session.state with details which capture user needs and confirm all details to the Orchestrator Agent."
    "Do NOT answer questions outside of budgeting. If asked, you must redirect to the relevant topic."
)

budget_agent = LlmAgent(
    name="BudgetAgent",
    model="gemini-1.5-flash",
    description="Handles budget management.",
    instruction=BUDGET_PROMPT,
    tools=[
        add_budget_item,
        get_budget_items,
        update_budget_item,
        delete_budget_item,
        get_user_data,
        update_user_data
    ],
<<<<<<< HEAD
    output_key="budget_state",

=======
    before_agent_callback=opik_tracer.before_agent_callback,
    after_agent_callback=opik_tracer.after_agent_callback,
    before_model_callback=opik_tracer.before_model_callback,
    after_model_callback=opik_tracer.after_model_callback,
    before_tool_callback=opik_tracer.before_tool_callback,
    after_tool_callback=opik_tracer.after_tool_callback,
>>>>>>> parent of 6547be4 (Refactor: Integrate DatabaseSessionService and improve DB handling)
)

VENDOR_PROMPT = (
    "You are the Vendor Search Agent for Sanskara AI. "
    "When invoked, always first check session.state for the user's preferences and a list of relevant vendor IDs. If this information is not available in session.state, fetch the user's preferences and all relevant user details from the users table."
    "Ask the user if they want to see any specific venue or filter vendors based on their saved preferences."
    "Use the user's preferences and details to suggest the most relevant vendors, and only ask for additional information if needed to refine the search."
    "Use your tools to list and get vendor details, and always validate input before constructing queries. "
    "All vendor operations are performed using robust, async tools that interact with Supabase via the MCP server, ensuring reliability and up-to-date information. "
    "If no vendors are found, always respond with a clear message such as 'No vendors found for your search.' or 'Not found.' "
    "Always check for errors in tool output and handle gracefully. "
    "Do NOT answer questions outside of vendor search. If asked, you must redirect to the relevant topic. "
    "if any question is not related to vendor search, transfer control to the orchestrator agent or relevant agent. "
    "When vendor search is complete, update session.state with a list of relevant vendor IDs and confirm all details to the Orchestrator Agent."

)

vendor_search_agent = LlmAgent(
    name="VendorSearchAgent",
    model="gemini-1.5-flash",
    description="Handles vendor search.",
    instruction=VENDOR_PROMPT,
    tools=[
        list_vendors,
        get_vendor_details
    ],
<<<<<<< HEAD
    output_key="vendor_search_state",
=======
    before_agent_callback=opik_tracer.before_agent_callback,
    after_agent_callback=opik_tracer.after_agent_callback,
    before_model_callback=opik_tracer.before_model_callback,
    after_model_callback=opik_tracer.after_model_callback,
    before_tool_callback=opik_tracer.before_tool_callback,
    after_tool_callback=opik_tracer.after_tool_callback,
>>>>>>> parent of 6547be4 (Refactor: Integrate DatabaseSessionService and improve DB handling)
)

# --- Root Agent ---

ORCHESTRATOR_PROMPT = (
    "You are the Orchestrator Agent for Sanskara AI. "
    "Ask user for their email address to start the onboarding process. "
    "Transfer control to the Onboarding Agent with the user's email address. "
    "You take over from the Onboarding Agent once onboarding is complete."
    "The user flow should follow these guidelines: 1. Upon receiving a user request, always check if the user's email is available. If not, prompt the user to provide it. 2. Verify that all required onboarding details are present. If any information is missing, guide the user through the onboarding process to collect it. 3. Once onboarding is complete, present the user with the following options: 'Budget Planning', 'Vendor Search', 'Ritual Information'. 4. Recommend a logical flow: 'Budget Planning' -> 'Vendor Search' -> 'Ritual Information'. However, allow the user to explore 'Vendor Search' and 'Ritual Information' at any time. 5. After each agent interaction, update the session state with relevant information to maintain context and improve future interactions. 6. If the user asks a question outside of the main workflow, answer it and then return to the previous state in the workflow. "
    "You coordinate with the Ritual, Budget, and Vendor agents as needed, gathering all required information from each and presenting it to the user. "
    "For each user request, determine which agent(s) can fulfill it, collect all required details, and present a concise, well-structured, and visually clean response that is precise to the user's question. "
    "Always present outputs in a clear, organized, and user-friendly format, summarizing and confirming actions taken. "
    "If more information is needed, ask the user for all missing details in as few steps as possible. "
    "Always pre-fill or infer information from previous answers or user data where possible. "
    "Never overwhelm the user with too many questions at once, but avoid unnecessary back-and-forth. "
    "Never expose internal logic or mention other agents by name. "
    "when the sub-agent completes its task, it should return control to you with the final response. "
    "If sub-agent are not able to answer or complete task even after using tools and available context , it should return control to orchestrator with feedback from its side. "
    "You are the main point of contact for the user, and all interactions should be seamless and intuitive."
    "You must ensure that the user has a smooth and efficient experience throughout the entire workflow."
    "Make sure sub-agents transfer control if the question is not related to budget management or it is more relevant to another agent."
    "Before transferring control to a sub-agent, check session.state for relevant information and pass it to the sub-agent. If the information is not in session.state, use your tools to retrieve it."
    "After a sub-agent completes its task, update session.state with the sub-agent's output."
)

root_agent = LlmAgent(
    name="RootAgent",
    model="gemini-1.5-flash",
    description="Orchestrates the entire user workflow for Sanskara AI, including onboarding, ritual search, budget management, and vendor search. The user only interacts with this agent.",
    instruction=ORCHESTRATOR_PROMPT,
    sub_agents=[
        onboarding_agent,
        ritual_search_agent,
        budget_agent,
        vendor_search_agent
    ],
<<<<<<< HEAD
    output_key="session_preferences",

=======
    before_agent_callback=opik_tracer.before_agent_callback,
    after_agent_callback=opik_tracer.after_agent_callback,
    before_model_callback=opik_tracer.before_model_callback,
    after_model_callback=opik_tracer.after_model_callback,
    before_tool_callback=opik_tracer.before_tool_callback,
    after_tool_callback=opik_tracer.after_tool_callback,
>>>>>>> parent of 6547be4 (Refactor: Integrate DatabaseSessionService and improve DB handling)
)


# Example usage (for testing):
if __name__ == "__main__":
    load_dotenv()
    async def run_agent():
        # --- Session Management ---
        session_service = InMemorySessionService()
        APP_NAME = "sanskara_ai"
        USER_ID = "user_123"
        SESSION_ID = "session_123"
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID
        )
        print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

        # --- Runner ---
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{runner.agent.name}'")
        print(f"GOOGLE_API_KEY loaded: {os.getenv('GOOGLE_API_KEY')}")
        messages= ['Hi','kpuneeth714@gmail.com','confirm','what is kanyadhanam ?']
        async def call_agent_async(query: str, runner, user_id, session_id):
            """Sends a query to the agent and prints the final response."""
            print(f"\n>>> User Query: {query}")
            content = types.Content(role='user', parts=[types.Part(text=query)])
            final_response_text = "Agent did not produce a final response."
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                # Uncomment to see all events:
                # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate:
                        final_response_text = f"Agent escalated: {getattr(event, 'error_message', 'No specific message.')}"
                    break
            #updated_session = await runner.session_service.get_session('sanskara_ai', user_id, session_id)
            #print(f"<<< Agent Response: {final_response_text}, Session State: {updated_session.state}")

        # Example interactive call
        for message in messages:
            await call_agent_async(message, runner, USER_ID, SESSION_ID)
        print("Agent run completed.")
    asyncio.run(run_agent())
