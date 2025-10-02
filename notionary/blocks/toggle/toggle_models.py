from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.models import Block
from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.blocks.types import BlockColor


class ToggleBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] = Field(default_factory=list)


class CreateToggleBlock(BaseModel):
    type: Literal["toggle"] = "toggle"
    toggle: ToggleBlock
