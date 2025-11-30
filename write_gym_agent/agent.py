import types
from google.adk.agents import Agent
from google.genai import types


from .specialized_agents.write_gym_workflow import write_gym_workflow
from google.adk.models.google_llm import Gemini
from configs.retry_config import retry_config


root_agent = Agent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="write_gym",
    sub_agents=[write_gym_workflow],
    description="Orchestrates the complete Write-Gym system.",
    instruction="""

You are the main orchestrator for a "Write Gym" writing-mentor system.

Step 1: USER SUBMITS TEXT
When a user provides text to analyze:
Pass the user_input to the write_gym_workflow subagent.

Step 2: Output
Wait for the write_gym_workflow subagent to finish. Capture its output.
Show user the output of the write_gym_workflow subagent.
""",
)

