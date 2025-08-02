from pydantic import BaseModel, Field
from typing_extensions import Literal

from notionary.blocks.rich_text.rich_text_models import RichTextObject


class EmbedBlock(BaseModel):
    url: str
    caption: list[RichTextObject] = Field(default_factory=list)


class CreateEmbedBlock(BaseModel):
    type: Literal["embed"] = "embed"
    embed: EmbedBlock
