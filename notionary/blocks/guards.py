from typing import Protocol

from notionary.blocks.models import BlockCreateRequest
from notionary.blocks.rich_text.rich_text_models import RichTextObject


class HasRichText(Protocol):
    """Protocol for objects that have a rich_text attribute."""

    rich_text: list[RichTextObject]


class HasChildren(Protocol):
    """Protocol for objects that have children blocks."""

    children: list[BlockCreateRequest]


class HasRichTextAndChildren(HasRichText, HasChildren, Protocol):
    """Protocol for objects that have both rich_text and children."""

    pass
