from pathlib import Path
import types
from google.adk.agents import Agent
from google.genai import types


from .specialized_agents.write_gym_text_lesson_workflow import write_gym_text_lesson_workflow
from google.adk.models.google_llm import Gemini
from .configs.retry_config import retry_config
from .specialized_agents.write_gym_daily_writing_lesson import (
    write_gym_daily_writing_lesson,
)

from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.models.google_llm import Gemini


from dotenv import load_dotenv

load_dotenv()


APP_NAME = "Write Gym"
write_gym_text_lesson_workflow = AgentTool(agent=write_gym_text_lesson_workflow)
write_gym_daily_lesson = AgentTool(agent=write_gym_daily_writing_lesson)
agent = Agent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="write_gym",
    tools=[write_gym_text_lesson_workflow, write_gym_daily_lesson],
    description="Orchestrates the complete Write-Gym system.",
    instruction="""

You are the main orchestrator for a "Write Gym" writing-mentor system.

SCENARIO 1 if USER SUBMITS TEXT TO analyze:
    Step 1:
    Pass the user_input to the write_gym_text_lesson_workflow tool.

    Step 2: Output
    Wait for the write_gym_text_lesson_workflow tool to finish. Capture its output.
    Return challenges from the the write_gym_text_lesson_workflow tool.
    IMPORTANT: RESPOND ONLY WITH CHALLENGES.

SCENARIO 2 if the user wants daily writing lesson:
    Step 1:
    Invoke the write_gym_daily_lesson tool.

    Step2:
    Wait for the write_gym_daily_lesson tool to finish. Capture its output.
    Return daily writing lesson from the the write_gym_daily_lesson tool.
    IMPORTANT: RESPOND ONLY WITH THE LESSON.

""",
)

root_agent = agent
