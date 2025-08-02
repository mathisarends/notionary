
from typing_extensions import Literal
from pydantic import BaseModel, Field
from notionary.blocks.shared.models import Block, BlockColor, RichTextObject


class NumberedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: list[Block] = Field(default_factory=list)

class CreateNumberedListItemBlock(BaseModel):
    type: Literal["numbered_list_item"] = "numbered_list_item"
    numbered_list_item: NumberedListItemBlock