from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.types import BlockColor


class ToDoBlock(BaseModel):
    rich_text: list[RichTextObject]
    checked: bool = False
    color: BlockColor = BlockColor.DEFAULT


class CreateToDoBlock(BaseModel):
    type: Literal["to_do"] = "to_do"
    to_do: ToDoBlock
