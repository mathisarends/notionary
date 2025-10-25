from enum import StrEnum
from typing import Literal

from pydantic import BaseModel

from notionary.shared.models.file import File


class IconType(StrEnum):
    EMOJI = "emoji"
    EXTERNAL = "external"
    FILE = "file"
    FILE_UPLOAD = "file_upload"


class EmojiIcon(BaseModel):
    type: Literal[IconType.EMOJI] = IconType.EMOJI
    emoji: str


type Icon = EmojiIcon | File
