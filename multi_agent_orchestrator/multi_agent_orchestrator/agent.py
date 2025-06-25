# main_orchestrator_agent.py - Main Orchestrator for the Sanskara AI application
import asyncio
from google.adk.runners import Runner # Will be needed for examples/testing, not directly by agent def
from google.adk.sessions import InMemorySessionService # Same as above
from dotenv import load_dotenv # For examples/testing
import os # For examples/testing

from google.adk.agents import LlmAgent
# Removed Event, EventActions, LlmRequest, LlmResponse, CallbackContext, InvocationContext if not directly used by OrchestratorAgent
# from google.adk.events import Event, EventActions
# from google.adk.models import LlmRequest,LlmResponse
# from google.adk.agents.callback_context import CallbackContext
# from google.adk.agents.invocation_context import InvocationContext
from typing import List, Dict, Any # Optional, Callable removed if not used
# from opik.integrations.adk import OpikTracer # OpikTracer removed for now
# from google.adk.planners import PlanReActPlanner # PlanReActPlanner removed for now
# from google.adk.memory import BaseMemoryService,InMemoryMemoryService # Memory services removed for now

from .sub_agents.onboarding import onboarding_agent
from .sub_agents.ritual_search import ritual_search_agent
from .sub_agents.budget import budget_agent
from .sub_agents.vendor_search import vendor_search_agent

# Import tools that the orchestrator itself might use (if any)
# For example, if timeline tools are directly used by the orchestrator
from .tools import create_timeline_event, get_timeline_events, update_timeline_event
# Assuming the orchestrator might need these. If not, this import can be removed.

from .prompt import ORCHESTRATOR_PROMPT # Import the prompt

import logging
from google.genai import types # For examples/testing

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Orchestrator Agent Definition ---

# Note: The sub_agents list will be populated after the sub_agents themselves are defined and imported.
# For now, it will be an empty list or commented out.
root_agent = LlmAgent(
    name="OrchestratorAgent", # Renamed from RootAgent
    model="gemini-2.0-flash",
    description="Orchestrates the entire user workflow for Sanskara AI, including onboarding, ritual search, budget management, and vendor search. The user only interacts with this agent.",
    instruction=ORCHESTRATOR_PROMPT,
    sub_agents=[
        onboarding_agent,
        ritual_search_agent,
        budget_agent,
        vendor_search_agent
    ],
    tools=[ # Adding timeline tools as per test implications
        create_timeline_event,
        get_timeline_events,
        update_timeline_event
    ],
    output_key="session_preferences",
)

# The old `if __name__ == "__main__":` block will be moved to an example script later.
# Sub-agent definitions (onboarding_agent, ritual_search_agent, etc.) are removed from here.
# Their respective PROMPT variables are also removed.
# Imports specific to sub-agents or their tools (like get_user_id from sanskara.tools) are removed from here.
