from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.blocks.types import BlockColor, BlockType


class ToDoBlock(BaseModel):
    rich_text: list[RichText]
    checked: bool = False
    color: BlockColor = BlockColor.DEFAULT


class CreateToDoBlock(BaseModel):
    type: Literal[BlockType.TO_DO] = BlockType.TO_DO
    to_do: ToDoBlock
