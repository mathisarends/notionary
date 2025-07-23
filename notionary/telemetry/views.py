from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass
class BaseTelemetryEvent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    def properties(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if k != "name"}


@dataclass
class DatabaseFactoryUsedEvent(BaseTelemetryEvent):
    """Event fired when a database factory method is used"""

    factory_method: str

    @property
    def name(self) -> str:
        return "database_factory_used"

@dataclass
class QueryOperationEvent(BaseTelemetryEvent):
    """Event fired when a query operation is performed"""

    query_type: str

    @property
    def name(self) -> str:
        return "query_operation"
    
@dataclass
class NotionMarkdownSyntaxPromptEvent(BaseTelemetryEvent):
    """Event fired when Notion Markdown syntax is used"""

    @property
    def name(self) -> str:
        return "notion_markdown_syntax_used"

# Tracks markdown conversion
@dataclass
class MarkdownToNotionConversionEvent(BaseTelemetryEvent):
    """Event fired when markdown is converted to Notion blocks"""
    handler_element_name: Optional[str] = None  # e.g. "HeadingElement", "ParagraphElement"
    
    @property
    def name(self) -> str:
        return "markdown_to_notion_conversion"


@dataclass
class NotionToMarkdownConversionEvent(BaseTelemetryEvent):
    """Event fired when Notion blocks are converted to markdown"""
    handler_element_name: Optional[str] = None  # e.g. "HeadingElement", "ParagraphElement"  
    
    @property
    def name(self) -> str:
        return "notion_to_markdown_conversion"