from abc import abstractmethod
from re import Match

from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.schemas import MentionType, RichText


class MentionPatternHandler(BasePatternHandler):
    @property
    @abstractmethod
    def mention_type(self) -> MentionType: ...

    @abstractmethod
    def create_mention(self, identifier: str) -> RichText: ...

    async def handle(self, match: Match) -> RichText:
        identifier = match.group(1)
        return self.create_mention(identifier)
