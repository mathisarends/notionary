from abc import ABC, abstractmethod

from notionary.page.content.syntax.service import SyntaxRegistry


class MarkdownNode(ABC):
    def __init__(self, syntax_registry: SyntaxRegistry | None = None) -> None:
        self._syntax_registry = syntax_registry or SyntaxRegistry()

    @abstractmethod
    def to_markdown(self) -> str:
        pass
