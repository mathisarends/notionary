from typing import Literal, Optional
from pydantic import BaseModel, Field

from notionary.blocks.shared.models import Block, BlockColor, IconObject, RichTextObject


class CalloutBlock(BaseModel):
    rich_text: list[RichTextObject]
    icon: Optional[IconObject] = None
    color: BlockColor = "default"
    children: list[Block] = Field(default_factory=list)


class CreateCalloutBlock(BaseModel):
    type: Literal["callout"] = "callout"
    callout: CalloutBlock
