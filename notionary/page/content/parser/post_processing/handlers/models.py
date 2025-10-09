from typing import Protocol

from notionary.blocks.rich_text.models import RichText
from notionary.blocks.schemas import BlockCreatePayload


class HasChildren(Protocol):
    children: list[BlockCreatePayload]


class HasRichText(Protocol):
    rich_text: list[RichText]
