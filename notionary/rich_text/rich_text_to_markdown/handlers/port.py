from abc import ABC, abstractmethod

from notionary.page.markdown.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.schemas import RichText


class RichTextHandler(ABC):
    def __init__(self) -> None:
        self._markdown_grammar = MarkdownGrammar()

    @abstractmethod
    def handle(self, rich_text: RichText) -> str:
        pass
