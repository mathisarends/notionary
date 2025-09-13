from __future__ import annotations
from typing import Literal, Union
from enum import StrEnum

from pydantic import BaseModel

from notionary.shared.models.file_models import ExternalFile, ExternalRessource


class IconType(StrEnum):
    EMOJI = "emoji"
    EXTERNAL = "external"


class EmojiIcon(BaseModel):
    type: Literal[IconType.EMOJI] = IconType.EMOJI
    emoji: str


# Basically ExternalRessource, but we redefine it here for clarity and better ide support
class ExternalIcon(BaseModel):
    type: Literal[IconType.EXTERNAL] = IconType.EXTERNAL
    external: ExternalFile


Icon = Union[EmojiIcon, ExternalIcon]
