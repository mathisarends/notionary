from abc import ABC, abstractmethod

from notionary.page.content.syntax import SyntaxDefinitionRegistry


class MarkdownNode(ABC):
    def __init__(self, syntax_registry: SyntaxDefinitionRegistry | None = None) -> None:
        self._syntax_registry = syntax_registry or SyntaxDefinitionRegistry()

    @abstractmethod
    def to_markdown(self) -> str:
        pass
