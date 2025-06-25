# agent.py - Orchestrator agent for the multi-agent system (migrated from sanskara/agent.py)
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv
import os
from google.adk.agents import Agent, SequentialAgent, LlmAgent
from google.adk.events import Event, EventActions
from google.adk.models import LlmRequest, LlmResponse
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator, List, Dict, Any, Optional, Callable
from opik.integrations.adk import OpikTracer
from google.adk.planners import PlanReActPlanner
from google.adk.memory import BaseMemoryService, InMemoryMemoryService
from multi_agent_orchestrator.tools import (
    get_user_id,
    get_user_data,
    update_user_data,
    list_vendors,
    get_vendor_details,
    add_budget_item,
    get_budget_items,
    update_budget_item,
    # delete_budget_item,  # Uncomment if implemented
    # search_rituals        # Uncomment if implemented
)
import logging
from google.genai import types
from .sub_agents.onboarding.agent import onboarding_agent
from .sub_agents.ritual_search.agent import ritual_search_agent
from .sub_agents.budget.agent import budget_agent
from .sub_agents.vendor_search.agent import vendor_search_agent
from multi_agent_orchestrator.prompt import ORCHESTRATOR_PROMPT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Sub-Agents ---
# Remove all prompt definitions here, use only the imported ones from sub-agent prompt.py files and orchestrator prompt.py

# Use sub-agents directly
root_agent = LlmAgent(
    name="RootAgent",
    model="gemini-2.0-flash",
    description="Orchestrates the entire user workflow for Sanskara AI, including onboarding, ritual search, budget management, and vendor search. The user only interacts with this agent.",
    instruction=ORCHESTRATOR_PROMPT,
    sub_agents=[onboarding_agent, ritual_search_agent, budget_agent, vendor_search_agent],
    output_key="session_preferences",
)

# Example usage (for testing):
if __name__ == "__main__":
    load_dotenv()
    async def run_agent():
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
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )
        print(f"Runner created for agent '{runner.agent.name}'")
        print(f"GOOGLE_API_KEY loaded: {os.getenv('GOOGLE_API_KEY')}")
        messages = ['Hi', 'kpuneeth714@gmail.com', 'confirm', 'what is kanyadhanam ?']
        async def call_agent_async(query: str, runner, user_id, session_id):
            print(f"\n>>> User Query: {query}")
            content = types.Content(role='user', parts=[types.Part(text=query)])
            final_response_text = "Agent did not produce a final response."
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.actions and event.actions.escalate:
                        final_response_text = f"Agent escalated: {getattr(event, 'error_message', 'No specific message.')}"
                    break
        for message in messages:
            await call_agent_async(message, runner, USER_ID, SESSION_ID)
        print("Agent run completed.")
    asyncio.run(run_agent())
