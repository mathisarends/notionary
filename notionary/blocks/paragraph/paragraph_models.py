from typing import Literal
from pydantic import BaseModel
from notionary.blocks.block_models import BlockColor
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class ParagraphBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"


class CreateParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    paragraph: ParagraphBlock
