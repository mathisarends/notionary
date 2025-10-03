from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.blocks.schemas import Block, BlockColor, BlockType
from notionary.shared.models.icon_models import Icon


class CalloutBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT
    icon: Icon | None = None
    children: list[Block] | None = None


class CreateCalloutBlock(BaseModel):
    type: Literal[BlockType.CALLOUT] = BlockType.CALLOUT
    callout: CalloutBlock
