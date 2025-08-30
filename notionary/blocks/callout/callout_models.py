from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, model_serializer

from notionary.blocks.file.file_element_models import FileBlock
from notionary.blocks.models import Block
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.types import BlockColor


class EmojiIcon(BaseModel):
    type: Literal["emoji"] = "emoji"
    emoji: str


class FileIcon(BaseModel):
    type: Literal["file"] = "file"
    file: FileBlock


IconObject = Union[EmojiIcon, FileIcon]


class CalloutBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT
    icon: Optional[IconObject] = None
    children: Optional[list[Block]] = None

class CreateCalloutBlock(BaseModel):
    type: Literal["callout"] = "callout"
    callout: CalloutBlock
