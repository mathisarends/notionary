from typing import Literal
from pydantic import BaseModel
from notionary.blocks.block_types import BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class ParagraphBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = BlockColor.DEFAULT


class CreateParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    paragraph: ParagraphBlock
