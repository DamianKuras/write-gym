import asyncio
import logging
import uuid
import gradio as gr
from pathlib import Path

from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types  # for Content & Part
from write_gym_agent.agent import root_agent
from dotenv import load_dotenv
from google.adk.memory import InMemoryMemoryService
from google.adk.plugins.logging_plugin import (
    LoggingPlugin,
)

load_dotenv()
logging.basicConfig(level=logging.INFO)

APP_NAME = "Write Gym"
db_dir = Path("data")
db_dir.mkdir(exist_ok=True)
db_path = db_dir / "agent_data.db"

session_service = DatabaseSessionService(db_url=f"sqlite+aiosqlite:///{db_path}")
memory_service = InMemoryMemoryService()
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
    plugins=[LoggingPlugin()],
)

USER_ID = "web_user"
SESSION_ID = "web_session"


async def maybe_create_session():
    """Ensure a session exists for the user + session_id."""
    try:
        # Attempt to create (or fetch) the session
        await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        logging.info(f"Session created: user_id={USER_ID}, session_id={SESSION_ID}")
    except Exception as e:
        logging.warning(f"Could not create session (maybe already exists): {e}")


async def process_text(user_input: str):
    if not user_input.strip():
        return "Please enter some text."

    logging.info(f"Processing: {user_input[:50]}...")

    # Make sure session exists (create if needed)
    await maybe_create_session()

    # Build the content object for the message
    content = types.Content(role="user", parts=[types.Part(text=user_input)])

    output = []
    try:
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            if getattr(event, "content", None) and event.content.parts:
                # Combine all text parts
                text = "".join(
                    [
                        part.text
                        for part in event.content.parts
                        if getattr(part, "text", None)
                    ]
                )
                output.append(text)
    except Exception as e:
        logging.exception(e)
        return f"An error occurred: {e}"

    return "\n".join(output) if output else "No output generated."


def create_ui():
    with gr.Blocks(title="Write Gym - Writing Mentor") as demo:
        gr.Markdown("# ✍️ Write Gym - Your Writing Mentor")
        gr.Markdown("Paste your text below for AI-powered writing feedback")

        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="Your Text",
                    placeholder="Paste your writing here...",
                    lines=10,
                )
                submit_btn = gr.Button("Analyze", variant="primary")

            with gr.Column():
                output = gr.Textbox(label="Feedback", lines=10, interactive=False)

        submit_btn.click(fn=process_text, inputs=text_input, outputs=output)

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.queue()
    demo.launch(share=False)
