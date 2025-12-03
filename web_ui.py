import asyncio
import logging
import uuid
import gradio as gr
from pathlib import Path

from google.adk.sessions import DatabaseSessionService
from google.adk.runners import Runner
from google.genai import types
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


async def process_text(text_input, audience_description):
    if not text_input.strip():
        return "Please enter some text."

    logging.info(f"Processing: {text_input[:50]}...")

    # Make sure session exists (create if needed)
    await maybe_create_session()

    message_text = f"""TEXT TO ANALYZE:
    {text_input}

    AUDIENCE DESCRIPTION:
    {audience_description if audience_description.strip() else "Not specified"}"""

    # Build the content object for the message
    output = []
    content = types.Content(role="user", parts=[types.Part(text=message_text)])
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


async def generate_daily_lesson():
    output = []
    content = types.Content(
        role="user", parts=[types.Part(text="Generate daily writing lesson")]
    )

    try:
        async for event in runner.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=content,
        ):
            if getattr(event, "content", None) and event.content.parts:
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
        return f"An error occurred generating your lesson: {e}"
    return "\n".join(output)


def create_ui():
    with gr.Blocks(
        title="Write Gym - Writing Mentor",
    ) as demo:
        with gr.Row():
            with gr.Column(scale=1):
                pass
            with gr.Column(scale=3):
                with gr.Tabs():
                    with gr.Tab("📝 Analyze My Writing"):
                        gr.Markdown(
                            "### Get Feedback on Your Writing\n"
                            "Submit your text and receive personalized feedback from our AI writing mentor."
                        )
                        text_input = gr.Textbox(
                            label="Your Text to analyze",
                            placeholder="Paste your writing here...",
                            lines=10,
                        )

                        audience_description_input = gr.Textbox(
                            label="Your target audience of your text to analyze, you might leave this empty to get automatic target audience detection.",
                            placeholder="This text is for general audience.",
                            lines=2,
                        )
                        submit_btn = gr.Button("Analyze", variant="primary")
                        with gr.Row():

                            output = gr.Markdown(
                                label="Feedback",
                                value="Your challenges will appear here...",
                                min_height=200,
                                padding=20,
                                container=True,
                            )
                            submit_btn.click(
                                fn=process_text,
                                inputs=[text_input, audience_description_input],
                                outputs=output,
                                show_progress="full",
                            )
                    with gr.Tab("🎓 Daily Writing Lesson"):
                        gr.Markdown("### Your Personalized Daily Writing Lesson\n")

                        generate_btn = gr.Button(
                            "Generate My Daily Lesson", variant="primary", size="lg"
                        )

                        lesson_output = gr.Markdown(
                            label="Your Daily Lesson",
                            value="Your personalized lesson will appear here...",
                            min_height=400,
                        )

                        generate_btn.click(
                            fn=generate_daily_lesson,
                            outputs=lesson_output,
                            show_progress="full",
                        )
            with gr.Column(scale=1):
                pass

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.queue()
    demo.launch(
        share=False,
    )
