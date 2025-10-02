from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel

from notionary.shared.models.file_models import ExternalFile


class IconType(StrEnum):
    EMOJI = "emoji"
    EXTERNAL = "external"


class EmojiIcon(BaseModel):
    type: Literal[IconType.EMOJI] = IconType.EMOJI
    emoji: str


class ExternalIcon(BaseModel):
    type: Literal[IconType.EXTERNAL] = IconType.EXTERNAL
    external: ExternalFile

    @classmethod
    def from_url(cls, url: str) -> Self:
        return cls(external=ExternalFile(url=url))


Icon = EmojiIcon | ExternalIcon
