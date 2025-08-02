from typing import Literal
from pydantic import BaseModel
from notionary.blocks.shared.models import BlockColor, RichTextObject


class ParagraphBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"


class CreateParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    paragraph: ParagraphBlock
