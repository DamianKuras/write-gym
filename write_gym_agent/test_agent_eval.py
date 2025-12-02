from google.adk.evaluation.agent_evaluator import AgentEvaluator
import pytest
import importlib
import sys
import os


@pytest.mark.asyncio
async def test_with_single_test_file():
    """Test the agent's basic ability via a session file."""
    # Load the agent module robustly
    module_name = "write_gym_agent.agent"
    try:
        agent_module = importlib.import_module(module_name)
        # Reset the mock data to ensure a fresh state for the test
        if hasattr(agent_module, "reset_mock_data"):
            agent_module.reset_mock_data()
    except ImportError:
        # Fallback if running from a different context
        sys.path.append(os.getcwd())
        agent_module = importlib.import_module(module_name)
        if hasattr(agent_module, "reset_mock_data"):
            agent_module.reset_mock_data()

    # Use absolute path to the eval file to be robust to where pytest is run
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eval_file = os.path.join(script_dir, "eval.test.json")

    await AgentEvaluator.evaluate(
        agent_module=module_name,
        eval_dataset_file_path_or_dir=eval_file,
        num_runs=1,
    )
