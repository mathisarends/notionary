from abc import ABC, abstractmethod

from notionary.shared.rich_text.schemas import RichText

from notionary.page.markdown.syntax.definition.grammar import MarkdownGrammar


class RichTextHandler(ABC):
    def __init__(self, markdown_grammar: MarkdownGrammar):
        self._markdown_grammar = markdown_grammar

    @abstractmethod
    async def handle(self, rich_text: RichText) -> str:
        pass
