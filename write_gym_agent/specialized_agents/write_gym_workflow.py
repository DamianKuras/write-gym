from .audience_detection_agent import audience_detection_agent
from .parallel_analysis_team_agent import parallel_analysis_team
from .feedback_aggregator import feedback_aggregator_agent
from google.adk.agents import SequentialAgent


write_gym_workflow = SequentialAgent(
    name="write_gym_workflow",
    description="Write gym workflow agent.",
    sub_agents=[
        audience_detection_agent,
        parallel_analysis_team,
        feedback_aggregator_agent,
    ],
)
