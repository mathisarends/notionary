# Import converters
from .markdown_to_notion_converter import MarkdownToNotionConverter
from .notion_to_markdown_converter import NotionToMarkdownConverter

from .registry.block_element_registry import BlockElementRegistry

# Import elements
from .elements.paragraph_element import ParagraphElement
from .elements.heading_element import HeadingElement
from .elements.callout_element import CalloutElement
from .elements.code_block_element import CodeBlockElement
from .elements.divider_element import DividerElement
from .elements.table_element import TableElement
from .elements.todo_lists import TodoElement
from .elements.list_element import BulletedListElement, NumberedListElement
from .elements.qoute_element import QuoteElement
from .elements.image_element import ImageElement
from .elements.video_element import VideoElement
from .elements.toggle_element import ToggleElement
from .elements.bookmark_element import BookmarkElement
from .elements.column_element import ColumnElement

# Register all elements
# Register paragraphs last since they're the fallback
BlockElementRegistry.register(HeadingElement)
BlockElementRegistry.register(CalloutElement)
BlockElementRegistry.register(CodeBlockElement)
BlockElementRegistry.register(DividerElement)
BlockElementRegistry.register(TableElement)
BlockElementRegistry.register(ColumnElement)
BlockElementRegistry.register(BulletedListElement)
BlockElementRegistry.register(NumberedListElement)
# Has to be registered before quote element
BlockElementRegistry.register(ToggleElement)
BlockElementRegistry.register(QuoteElement)
BlockElementRegistry.register(TodoElement)
BlockElementRegistry.register(BookmarkElement)
BlockElementRegistry.register(ImageElement)
BlockElementRegistry.register(VideoElement)
# Register last! (Fallback)
BlockElementRegistry.register(ParagraphElement)

# Define what to export
__all__ = [
    "BlockElementRegistry",
    "MarkdownToNotionConverter",
    "NotionToMarkdownConverter",
    "ParagraphElement",
    "HeadingElement",
    "CalloutElement",
    "CodeBlockElement",
    "DividerElement",
    "TableElement",
    "TodoElement",
    "QuoteElement",
    "BulletedListElement",
    "NumberedListElement",
]
