from abc import abstractmethod
from re import Match

from notionary.rich_text.markdown_to_rich_text.handlers.base import BasePatternHandler
from notionary.rich_text.schemas import MentionType, RichText
from notionary.shared.name_id_resolver import NameIdResolver


class MentionPatternHandler(BasePatternHandler):
    def __init__(self, resolver: NameIdResolver) -> None:
        self._resolver = resolver

    @property
    @abstractmethod
    def mention_type(self) -> MentionType: ...

    @abstractmethod
    def create_mention(self, resolved_id: str) -> RichText: ...

    async def handle(self, match: Match) -> RichText:
        identifier = match.group(1)
        return await self._create_mention_or_fallback(identifier)

    async def _create_mention_or_fallback(self, identifier: str) -> RichText:
        try:
            resolved_id = await self._resolver.resolve_name_to_id(identifier)

            if resolved_id:
                return self.create_mention(resolved_id)
            else:
                return self._create_unresolved_mention_fallback(identifier)

        except Exception:
            return self._create_unresolved_mention_fallback(identifier)

    def _create_unresolved_mention_fallback(self, identifier: str) -> RichText:
        fallback_text = f"@{self.mention_type.value}[{identifier}]"
        return RichText.for_caption(fallback_text)
