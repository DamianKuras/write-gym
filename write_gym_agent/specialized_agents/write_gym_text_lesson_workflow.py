from .audience_router_agent import audience_router
from .parallel_analysis_team_agent import parallel_analysis_team
from .feedback_aggregator import feedback_aggregator_agent
from google.adk.agents import SequentialAgent


write_gym_text_lesson_workflow = SequentialAgent(
    name="write_gym_text_lesson_workflow",
    description="Write gym text lesson workflow agent.",
    sub_agents=[
        audience_router,
        parallel_analysis_team,
        feedback_aggregator_agent,
    ],
)
