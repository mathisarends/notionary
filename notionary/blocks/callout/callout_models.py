from typing import Literal, Optional
from pydantic import BaseModel, Field

from notionary.blocks.block_models import Block, BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.models.icon_types import IconObject


class CalloutBlock(BaseModel):
    rich_text: list[RichTextObject]
    icon: Optional[IconObject] = None
    color: BlockColor = "default"
    children: list[Block] = Field(default_factory=list)


class CreateCalloutBlock(BaseModel):
    type: Literal["callout"] = "callout"
    callout: CalloutBlock
