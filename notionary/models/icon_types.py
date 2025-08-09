from typing import Union, Literal
from pydantic import BaseModel

from notionary.blocks.file.file_element_models import FileBlock


class EmojiIcon(BaseModel):
    type: Literal["emoji"] = "emoji"
    emoji: str


class FileIcon(BaseModel):
    type: Literal["file"] = "file"
    file: FileBlock


IconObject = Union[EmojiIcon, FileIcon]
