from abc import ABC, abstractmethod
from re import Match, Pattern

from notionary.rich_text.schemas import RichText


class BasePatternHandler(ABC):
    @property
    @abstractmethod
    def pattern(self) -> Pattern: ...

    @abstractmethod
    async def handle(self, match: Match) -> RichText | list[RichText]: ...
