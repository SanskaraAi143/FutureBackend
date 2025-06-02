# agents.py - ADK agents for the Sanskara AI application
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv
import os

from google.adk.agents import Agent, SequentialAgent, LlmAgent,Agent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, List, Dict, Any, Optional
from .tools import (
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
    "You are the Onboarding Agent for Sanskara AI. "
    "Your job is to collect and confirm all required user details for wedding planning in as few steps as possible. "
    "When requesting information, always ask for multiple related fields together (e.g., name, email, wedding date, culture, region, etc.) to minimize back-and-forth. "
    "If any information is already available, use it to pre-fill or skip questions. "
    "IMPORTANT: Only write to the following top-level fields in the users table: display_name, wedding_date, wedding_location, wedding_tradition, user_type. All other user attributes (such as caste, culture, region, budget, guest count, etc.) MUST be stored inside the preferences dictionary. Do NOT attempt to write any other fields at the top level. "
    "You must collect and confirm: full name, email, wedding date (or preferred month/year), culture, caste, region, estimated budget, guest count, and location. "
    "Do NOT allow the process to proceed to vendor, budget, or ritual steps until ALL onboarding fields are complete and confirmed. "
    "Always use your tools to fetch, update, and pre-populate user data. "
    "When onboarding is complete, clearly confirm all collected details. "
)

onboarding_agent = LlmAgent(
    name="OnboardingAgent",
    model="gemini-2.0-flash",
    description="Handles user onboarding.",
    instruction=ONBOARDING_PROMPT,
    tools=[get_user_id, get_user_data, update_user_data]
)

RITUAL_PROMPT = (
    "You are the Ritual Agent for Sanskara AI. "
    "Your job is to provide clear, concise, and culturally accurate information about Hindu wedding rituals, based strictly on the user's culture, caste, and region. "
    "List the most relevant rituals, explain their significance, and answer questions about them. "
    "If asked for samagri (items) or specific timings, explain that a Pandit should be consulted for exact details. "
    "Use your tools to search for rituals in the database. "
    "Never answer questions outside of rituals. If asked, politely redirect to the relevant topic. "
    "Always format your answers for clarity and completeness. "
)

ritual_search_agent = LlmAgent(
    name="RitualSearchAgent",
    model="gemini-2.0-flash",
    description="Handles ritual search.",
    instruction=RITUAL_PROMPT,
    tools=[search_rituals]
)

BUDGET_PROMPT = (
    "You are the Budget Agent for Sanskara AI. "
    "Your job is to help set a realistic, itemized wedding budget and suggest allocations by category (venue, catering, decor, etc.). "
    "ALWAYS ask for total budget, number of events, and region if not already collected, and try to collect these in a single step if possible. "
    "Use your tools to add, get, update, and delete budget items, and to fetch user preferences. "
    "Do NOT answer questions outside of budgeting. If asked, politely redirect to the relevant topic. "
    "When budget setup is complete, confirm all details. "
)

budget_agent = LlmAgent(
    name="BudgetAgent",
    model="gemini-2.0-flash",
    description="Handles budget management.",
    instruction=BUDGET_PROMPT,
    tools=[
        add_budget_item,
        get_budget_items,
        update_budget_item,
        delete_budget_item,
        get_user_data,
        update_user_data
    ]
)

VENDOR_PROMPT = (
    "You are the Vendor Search Agent for Sanskara AI. "
    "Your job is to help specify and refine preferences for wedding vendors (venue, photographer, caterer, etc.). "
    "ALWAYS ask for location, style, budget per category, and any special requirements, and try to collect these in a single step if possible. "
    "Use your tools to search and fetch vendor details. "
    "Never answer questions outside of vendor search and preferences. If asked, politely redirect to the relevant topic. "
    "When vendor preferences are finalized, confirm all details. "
)

vendor_search_agent = LlmAgent(
    name="VendorSearchAgent",
    model="gemini-2.0-flash",
    description="Handles vendor search.",
    instruction=VENDOR_PROMPT,
    tools=[
        list_vendors,
        get_vendor_details
    ]
)

# --- Root Agent ---

ORCHESTRATOR_PROMPT = (
    "You are the Orchestrator Agent for Sanskara AI. "
    "You are the ONLY agent the user interacts with directly. "
    "You must act as a friendly, efficient, and helpful wedding planning assistant. "
    "Do NOT transfer the user to other agents or mention sub-agents. Instead, gather all user input, and internally coordinate with onboarding, ritual, vendor, and budget agents as needed. "
    "Minimize the number of follow-up questions: try to collect all required information in as few steps as possible, using clear, concise, and friendly prompts. "
    "If you need more than one piece of information, ask for them together in a single message. "
    "Always pre-fill or infer information from previous answers or user data where possible. "
    "Never overwhelm the user with too many questions at once, but avoid unnecessary back-and-forth. "
    "After onboarding, let the user choose what to do next (vendors, budget, rituals, etc.), and handle their requests smoothly. "
    "Always summarize and confirm actions taken, and keep the conversation natural and user-friendly. "
    "Never expose internal logic or mention other agents. "
)

root_agent = LlmAgent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Orchestrates the entire user workflow for Sanskara AI, including onboarding, ritual search, budget management, and vendor search. The user only interacts with this agent.",
    instruction=ORCHESTRATOR_PROMPT,
    sub_agents=[
        onboarding_agent,
        ritual_search_agent,
        budget_agent,
        vendor_search_agent
    ]
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
            print(f"<<< Agent Response: {final_response_text}")

        # Example interactive call
        await call_agent_async("What is kanyadhanam ?", runner, USER_ID, SESSION_ID)

    asyncio.run(run_agent())
