from abc import ABC, abstractmethod

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.rich_text.schemas import Mention


class MentionHandler(ABC):
    def __init__(self, markdown_grammar: MarkdownGrammar):
        self._markdown_grammar = markdown_grammar

    @abstractmethod
    async def handle(self, mention: Mention) -> str:
        pass

    def _format_mention(self, prefix: str, name: str) -> str:
        return f"{prefix}{name}{self._markdown_grammar.mention_suffix}"
