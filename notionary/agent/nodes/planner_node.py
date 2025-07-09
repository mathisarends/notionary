from textwrap import dedent
from notionary.agent.models import AgentState, PlannerResponse
from notionary.agent.nodes.base_node import GraphNode

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage


class PlannerNode(GraphNode):
    def __init__(self, planner_llm: BaseChatModel):
        self.planner_llm = planner_llm.with_structured_output(PlannerResponse)

    async def __call__(self, state: AgentState) -> dict:
        """Call the planner LLM to generate a plan based on the current state."""
        system_prompt = dedent(
            """You are a strategic planner for a Notion agent. Your task is to create a clear, actionable plan based on the current state.

            YOUR ROLE:
            - Analyze the current situation objectively
            - Evaluate progress towards goal completion
            - Identify challenges and obstacles
            - Define concrete, prioritized next steps
            - Provide logical reasoning for your decisions

            CONTEXT:
            The agent works with Notion databases, pages, and content. Typical tasks include:
            - Creating, editing, searching Notion pages
            - Database operations (querying, filtering, updating)
            - Content extraction and analysis
            - Workflow automation

            INSTRUCTIONS:
            1. Analyze the current status factually and precisely
            2. Evaluate progress: What has been achieved? What is still missing?
            3. Identify concrete obstacles or problems
            4. Prioritize steps by importance and dependencies
            5. Explain your reasoning and prioritization

            OUTPUT:
            Structured response with clear action recommendations."""
        )

        human_prompt = dedent(
            f"""CURRENT TASK: {state.task}

            CURRENT STATUS:
            - Step Number: {state.n_steps}
            - Last Result: {state.last_result or "No result yet"}
            - Previous Steps: {len(state.agent_steps)}
            - Errors: {state.errors if state.errors else "None"}
            - Memory: {state.memory or "This is your first step towards task completion"}

            PREVIOUS ACTIONS:
            {self._format_previous_actions(state)}

            Based on this information, create a strategic plan for the next steps."""
        )

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]

        response = await self.planner_llm.ainvoke(messages)

        self.logger.info(f"Planner response: {response}")

        return response.dict()

    def _format_previous_actions(self, state: AgentState) -> str:
        """Format previous actions for context."""
        if not state.agent_steps:
            return "No previous actions"

        formatted = []
        for i, step in enumerate(state.agent_steps[-3:], 1):  # Last 3 steps for context
            if step.model_output:
                actions = [
                    (
                        action.action_type
                        if hasattr(action, "action_type")
                        else str(action)
                    )
                    for action in step.model_output.action
                ]
                formatted.append(f"Step {i}: {', '.join(actions)}")

        return "\n".join(formatted) if formatted else "No evaluable actions"
