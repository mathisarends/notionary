from typing import Literal

from pydantic import BaseModel

from notionary.blocks.rich_text.models import RichText
from notionary.blocks.types import BlockColor, BlockType


class ParagraphBlock(BaseModel):
    rich_text: list[RichText]
    color: BlockColor = BlockColor.DEFAULT.value


class CreateParagraphBlock(BaseModel):
    type: Literal[BlockType.PARAGRAPH] = BlockType.PARAGRAPH
    paragraph: ParagraphBlock
