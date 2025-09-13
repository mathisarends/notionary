from __future__ import annotations
from typing import Literal, Union
from enum import StrEnum

from pydantic import BaseModel
from notionary.shared.models.file_models import ExternalFile

class IconType(StrEnum):
    EMOJI = "emoji"
    EXTERNAL = "external"


class EmojiIcon(BaseModel):
    type: Literal[IconType.EMOJI] = IconType.EMOJI
    emoji: str


class ExternalRessource(BaseModel):
    type: Literal[IconType.EXTERNAL] = IconType.EXTERNAL
    external: ExternalFile

    @classmethod
    def from_url(cls, url: str) -> ExternalRessource:
        return cls(external=ExternalFile(url=url))


Icon = Union[EmojiIcon, ExternalRessource]