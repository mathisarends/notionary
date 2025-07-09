from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel

from notionary.agent.models import AgentSettings
from notionary.util import LoggingMixin


class NotionAgent(LoggingMixin):
    def __init__(
        self,
        task: str,
        chat_mode: BaseChatModel,
        content_extraction_llm: BaseChatModel | None = None,
        planner_llm: BaseChatModel | None = None,
        planner_interval: int = 1,
    ):
        self.task = task
        self.chat_mode = chat_mode

        self.settings = AgentSettings(
            content_extraction_llm=content_extraction_llm,
            planner_llm=planner_llm,
            planner_interval=planner_interval,
        )

    async def run(self) -> None:
        """Run the agent to complete the task."""
        self.logger.info(f"Starting agent for task: {self.task}")

        self.logger.info(
            f"Task '{self.task}' is being processed with settings: {self.settings}"
        )

        # Simulate some processing
        await self.process_task()
