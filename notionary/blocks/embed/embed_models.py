from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.rich_text.rich_text_models import RichText


class EmbedBlock(BaseModel):
    url: str
    caption: list[RichText] = Field(default_factory=list)


class CreateEmbedBlock(BaseModel):
    type: Literal["embed"] = "embed"
    embed: EmbedBlock
