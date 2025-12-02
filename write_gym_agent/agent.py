from pathlib import Path
import types
from google.adk.agents import Agent
from google.genai import types


from .specialized_agents.write_gym_workflow import write_gym_workflow
from google.adk.models.google_llm import Gemini
from .configs.retry_config import retry_config

from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.models.google_llm import Gemini


from dotenv import load_dotenv

load_dotenv()


APP_NAME = "Write Gym"
write_gym = AgentTool(agent=write_gym_workflow)
agent = Agent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="write_gym",
    tools=[write_gym],
    description="Orchestrates the complete Write-Gym system.",
    instruction="""

You are the main orchestrator for a "Write Gym" writing-mentor system.

Step 1: USER SUBMITS TEXT TO analyze
When a user provides text to analyze:
Pass the user_input to the write_gym_workflow tool.


Step 2: Output
Wait for the write_gym_workflow subagent to finish. Capture its output.
Return challenges from the the write_gym_workflow tool.
IMPORTANT: RESPOND ONLY WITH CHALLENGES.

""",
)

root_agent = agent
