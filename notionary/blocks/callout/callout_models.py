from typing import Literal

from pydantic import BaseModel

from notionary.blocks.models import Block
from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.blocks.types import BlockColor
from notionary.shared.models.icon_models import Icon


class CalloutBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    icon: Icon | None = None
    children: list[Block] | None = None


class CreateCalloutBlock(BaseModel):
    type: Literal["callout"] = "callout"
    callout: CalloutBlock
