from typing import Literal
from pydantic import BaseModel
from notionary.blocks.block_models import BlockColor, RichTextObject


class ParagraphBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"


class CreateParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    paragraph: ParagraphBlock
