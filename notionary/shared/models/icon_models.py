from __future__ import annotations
from typing import Literal, Union
from enum import StrEnum

from pydantic import BaseModel

from notionary.blocks.file.file_element_models import FileBlock
from notionary.shared.models.file_models import ExternalRessource


class IconType(StrEnum):
    EMOJI = "emoji"
    FILE = "file"
    EXTERNAL = "external"


class EmojiIcon(BaseModel):
    type: Literal[IconType.EMOJI] = IconType.EMOJI
    emoji: str


class FileIcon(BaseModel):
    type: Literal[IconType.FILE] = IconType.FILE
    file: FileBlock


ExternalIcon = ExternalRessource

Icon = Union[EmojiIcon, FileIcon, ExternalRessource]


# ---
# DTOs (e.g. for updating a page's icon)
class UpdateIconDto(BaseModel):
    icon: Icon | None = None

    @classmethod
    def from_url(cls, url: str) -> UpdateIconDto:
        return cls(icon=ExternalRessource.from_url(url))

    @classmethod
    def from_emoji(cls, emoji: str) -> UpdateIconDto:
        return cls(icon=EmojiIcon(emoji=emoji))
