from typing import Literal
from pydantic import BaseModel, Field

from notionary.blocks.shared.models import Block, BlockColor, RichTextObject


class ToDoBlock(BaseModel):
    rich_text: list[RichTextObject]
    checked: bool = False
    color: BlockColor = "default"
    children: list[Block] = Field(default_factory=list)


class CreateToDoBlock(BaseModel):
    type: Literal["to_do"] = "to_do"
    to_do: ToDoBlock
