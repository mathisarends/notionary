from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from notionary.shared.object.schemas import File


class IconType(StrEnum):
    EMOJI = "emoji"
    CUSTOM_EMOJI = "custom_emoji"
    ICON = "icon"
    EXTERNAL = "external"
    FILE = "file"
    FILE_UPLOAD = "file_upload"


class EmojiIcon(BaseModel):
    type: Literal[IconType.EMOJI] = IconType.EMOJI
    emoji: str


class CustomEmojiData(BaseModel):
    id: UUID
    name: str | None = None
    url: str | None = None


class CustomEmojiIcon(BaseModel):
    type: Literal[IconType.CUSTOM_EMOJI] = IconType.CUSTOM_EMOJI
    custom_emoji: CustomEmojiData


class BuiltinIconColor(StrEnum):
    GRAY = "gray"
    LIGHT_GRAY = "lightgray"
    BROWN = "brown"
    YELLOW = "yellow"
    ORANGE = "orange"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    PINK = "pink"
    RED = "red"


class BuiltinIconData(BaseModel):
    name: str
    color: BuiltinIconColor = BuiltinIconColor.GRAY


class BuiltinIcon(BaseModel):
    type: Literal[IconType.ICON] = IconType.ICON
    icon: BuiltinIconData


type AnyIcon = Annotated[
    EmojiIcon | CustomEmojiIcon | BuiltinIcon | File,
    Field(discriminator="type"),
]
