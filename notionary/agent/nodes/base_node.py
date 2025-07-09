import re
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Protocol, Dict, Any, Union, Mapping
from util.logging_mixin import LoggingMixin


class GraphState(Protocol):
    """Protocol defining the minimal interface for graph states."""


StateType = TypeVar("StateType", bound=GraphState)
PartialStateType = TypeVar("PartialStateType", bound=Dict[str, Any])


class GraphNode(LoggingMixin, Generic[StateType], ABC):
    """Base class for all workflow graph nodes with automatic NODE_NAME generation."""

    NODE_NAME: str = "base_graph_node"

    def __init_subclass__(cls, **kwargs):
        """Automatically generate NODE_NAME from class name if not explicitly set."""
        super().__init_subclass__(**kwargs)

        # Skip validation for abstract base classes
        if ABC in cls.__bases__:
            return

        # Check if NODE_NAME was explicitly overridden in this class
        # (not inherited from parent)
        has_explicit_node_name = "NODE_NAME" in cls.__dict__

        if not has_explicit_node_name:
            cls.NODE_NAME = cls._class_name_to_snake_case(cls.__name__)

        if not isinstance(cls.NODE_NAME, str):
            raise TypeError(f"NODE_NAME must be a string, got {type(cls.NODE_NAME)}")

        if not cls.NODE_NAME.strip():
            raise ValueError(f"NODE_NAME cannot be empty in {cls.__name__}")

    @staticmethod
    def _class_name_to_snake_case(class_name: str) -> str:
        """
        Convert CamelCase class name to snake_case.

        Examples:
            GraphNode -> graph_node
            ProcessDataNode -> process_data_node
            XMLHttpRequestHandler -> xml_http_request_handler
            HTMLParser -> html_parser
        """
        # Handle sequences of uppercase letters (like XML, HTTP)
        # Insert underscore before uppercase letter that follows lowercase
        s1 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", class_name)

        s2 = re.sub("([A-Z])([A-Z][a-z])", r"\1_\2", s1)

        return s2.lower()

    @abstractmethod
    async def __call__(self, state: StateType) -> Union[StateType, Mapping[str, Any]]:
        """
        Process the node's logic and return updated state.

        Returns:
            Either the full state or a partial state dictionary with only changed fields.
        """
