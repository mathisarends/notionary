from typing import Protocol, TypeGuard

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


def is_rich_text_container(obj: object) -> TypeGuard[HasRichText]:
    """Type guard to check if an object has rich_text attribute."""
    return hasattr(obj, "rich_text") and isinstance(getattr(obj, "rich_text"), list)


def is_children_container(obj: object) -> TypeGuard[HasChildren]:
    """Type guard to check if an object has children attribute."""
    return hasattr(obj, "children") and isinstance(getattr(obj, "children"), list)


def is_text_rich_text_object(rich_text_obj: RichTextObject) -> TypeGuard[RichTextObject]:
    """Type guard to check if a RichTextObject is of type 'text' with content."""
    return (
        rich_text_obj.type == "text" 
        and rich_text_obj.text is not None
        and rich_text_obj.text.content is not None
    )