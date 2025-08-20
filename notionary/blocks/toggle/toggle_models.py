from pydantic import BaseModel, Field
from typing_extensions import Literal

from notionary.blocks.models import Block
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.blocks.types import BlockColor


class ToggleBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT
    children: list[Block] = Field(default_factory=list)


class CreateToggleBlock(BaseModel):
    type: Literal["toggle"] = "toggle"
    toggle: ToggleBlock
