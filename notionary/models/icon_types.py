from typing import Union, Literal
from pydantic import BaseModel

from notionary.blocks.file.file_element_models import FileObject


class EmojiIcon(BaseModel):
    type: Literal["emoji"] = "emoji"
    emoji: str


class FileIcon(BaseModel):
    type: Literal["file"] = "file"
    file: FileObject


IconObject = Union[EmojiIcon, FileIcon]
