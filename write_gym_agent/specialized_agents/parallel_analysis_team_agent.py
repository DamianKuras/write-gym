from google.adk.agents import ParallelAgent

from .audience_fit_analysis_agent import audience_fit_analysis_agent

from .style_agent import style_agent
from .readability_agent import readability_agent
from .originality_check_agent import originality_check_agent

parallel_analysis_team = ParallelAgent(
    name="write_gym_analysis",
    sub_agents=[
        audience_fit_analysis_agent,
        style_agent,
        readability_agent,
        originality_check_agent,
    ],
)
