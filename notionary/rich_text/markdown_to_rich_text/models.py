from collections.abc import Callable
from dataclasses import dataclass
from re import Match

from notionary.rich_text.schemas import RichText


@dataclass
class PatternMatch:
    match: Match
    handler: Callable[[Match], RichText | list[RichText]]
    position: int

    @property
    def matched_text(self) -> str:
        return self.match.group(0)

    @property
    def end_position(self) -> int:
        return self.position + len(self.matched_text)


@dataclass
class PatternHandler:
    pattern: str
    handler: Callable[[Match], RichText | list[RichText]]
