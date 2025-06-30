
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import os

from multi_agent_orchestrator.agent import root_agent


async def main():
    """Runs the orchestrator agent."""
    load_dotenv()

    # Get the Google API key from the environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

    # Create a runner for the agent
    runner = Runner(
        agent=root_agent,
        session_service=InMemorySessionService(),
        api_key=google_api_key,
    )

    # Run the agent
    print("Running orchestrator agent...")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        response = await runner.run(user_input)
        print(f"Agent: {response}")


if __name__ == "__main__":
    asyncio.run(main())
