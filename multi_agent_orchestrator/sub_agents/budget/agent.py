from google.adk.agents import LlmAgent
from .prompt import BUDGET_PROMPT

from multi_agent_orchestrator.tools import (
    add_budget_item,
    get_budget_items,
    update_budget_item,
    delete_budget_item,
    get_user_data,
    update_user_data
)
# No longer need placeholders

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
    ],
    output_key="budget_state",
)
