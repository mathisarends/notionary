from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from notionary.blocks.block_models import RichTextObject, BlockColor

# ============================================================================
# HEADING BLOCK DATA MODELS
# ============================================================================


class Heading1Block(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    is_toggleable: bool = False
    children: list["Block"] = Field(default_factory=list)


class Heading2Block(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    is_toggleable: bool = False
    children: list["Block"] = Field(default_factory=list)


class Heading3Block(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    is_toggleable: bool = False
    children: list["Block"] = Field(default_factory=list)


# ============================================================================
# HEADING CREATE REQUEST MODELS
# ============================================================================


class CreateHeading1Block(BaseModel):
    type: Literal["heading_1"] = "heading_1"
    heading_1: Heading1Block


class CreateHeading2Block(BaseModel):
    type: Literal["heading_2"] = "heading_2"
    heading_2: Heading2Block


class CreateHeading3Block(BaseModel):
    type: Literal["heading_3"] = "heading_3"
    heading_3: Heading3Block
