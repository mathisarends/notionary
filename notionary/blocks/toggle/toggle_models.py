from typing_extensions import Literal
from pydantic import BaseModel, Field

from notionary.blocks.block_models import Block, BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class ToggleBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: list[Block] = Field(default_factory=list)


class CreateToggleBlock(BaseModel):
    type: Literal["toggle"] = "toggle"
    toggle: ToggleBlock
