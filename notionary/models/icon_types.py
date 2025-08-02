from typing import Union
from pydantic import BaseModel
from typing_extensions import Literal

from notionary.blocks.file.file_element_models import FileObject


class EmojiIcon(BaseModel):
    type: Literal["emoji"] = "emoji"
    emoji: str


class FileIcon(BaseModel):
    type: Literal["file"] = "file"
    file: FileObject


IconObject = Union[EmojiIcon, FileIcon]
