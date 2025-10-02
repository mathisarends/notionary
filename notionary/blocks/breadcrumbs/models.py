from typing import Literal

from pydantic import BaseModel

from notionary.blocks.types import BlockType


class BreadcrumbBlock(BaseModel):
    pass


class CreateBreadcrumbBlock(BaseModel):
    type: Literal[BlockType.BREADCRUMB] = BlockType.BREADCRUMB
    breadcrumb: BreadcrumbBlock
