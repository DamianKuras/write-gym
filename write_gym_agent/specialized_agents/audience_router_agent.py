from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import AgentTool
from .audience_detection_agent import audience_detection_agent
from .parallel_analysis_team_agent import parallel_analysis_team
from .feedback_aggregator import feedback_aggregator_agent
from google.adk.models.google_llm import Gemini
from ..configs.retry_config import retry_config

# Create a conditional router
audience_router = Agent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="audience_router",
    tools=[AgentTool(agent=audience_detection_agent)],
    description="Routes to audience detection if needed.",
    instruction="""Check the message:
- If AUDIENCE says "Detect automatically", call the audience_detection_agent
- Otherwise, note the provided audience and skip detection
Pass the audience (detected or provided) forward.""",
)
