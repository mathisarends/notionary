from typing import Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field

from langchain_core.language_models.chat_models import BaseChatModel

class PlannerResponse(BaseModel):
    state_analysis: str
    progress_evaluation: str
    challenges: List[str]
    next_steps: List[str]
    reasoning: str
    
    
class AgentSettings(BaseModel):
	"""Configuration options for the Agent"""
	override_system_message: str | None = None
	extend_system_message: str | None = None
	max_actions_per_step: int = 5
	use_thinking: bool = True
	max_history_items: int = 40

	content_extraction_llm: BaseChatModel | None = None
	planner_llm: BaseChatModel | None = None
	planner_interval: int = 1
	extend_planner_system_message: str | None = None
    
class AgentBrain(BaseModel):
	thinking: str | None = None
	evaluation_previous_goal: str
	memory: str
	next_goal: str
 
 
# Action Model has to be defined here
class AgentOutput(BaseModel):
	model_config = ConfigDict(arbitrary_types_allowed=True, extra='forbid')

	thinking: str | None = None
	evaluation_previous_goal: str
	memory: str
	next_goal: str
	action: list[ActionModel] = Field(
		...,
		description='List of actions to execute',
		json_schema_extra={'min_items': 1}, 
	)
    
    
class ActionResult(BaseModel):
	is_done: bool | None = False
	is_successful: bool | None = None

	error: str | None = NotImplemented
    output: Union[str, Dict]
	extracted_content: str | None = None
 

class AgentStep(BaseModel):
	"""History item for agent actions"""

	model_output: AgentOutput | None
	result: list[ActionResult]

	model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())
 
 
class AgentState(BaseModel):
    user_input: str
    n_steps: int = 1
    last_result: Optional[str] = None
    plan: Optional[PlannerResponse] = None
    action_result: Optional[ToolResult] = None
    errors: List[str] = Field(default_factory=list)

    agent_steps: List[AgentStep] = Field(default_factory=list)

    last_model_output: AgentOutput | None = None