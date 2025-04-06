# Import converters
from .markdown_to_notion_converter import MarkdownToNotionConverter
from .notion_to_markdown_converter import NotionToMarkdownConverter

from .registry.notion_element_registry import ElementRegistry

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
ElementRegistry.register(HeadingElement)
ElementRegistry.register(CalloutElement)
ElementRegistry.register(CodeBlockElement)
ElementRegistry.register(DividerElement)
ElementRegistry.register(TableElement)
ElementRegistry.register(ColumnElement)
ElementRegistry.register(BulletedListElement)
ElementRegistry.register(NumberedListElement)
# Has to be registered before quote element
ElementRegistry.register(ToggleElement) 
ElementRegistry.register(QuoteElement)
ElementRegistry.register(TodoElement)
ElementRegistry.register(BookmarkElement)
ElementRegistry.register(ImageElement)
ElementRegistry.register(VideoElement)
# Register last! (Fallback)
ElementRegistry.register(ParagraphElement)

# Define what to export
__all__ = [
    'ElementRegistry',
    'MarkdownToNotionConverter',
    'NotionToMarkdownConverter',
    'ParagraphElement',
    'HeadingElement',
    'CalloutElement',
    'CodeBlockElement',
    'DividerElement',
    'TableElement',
    'TodoElement',
    'QuoteElement',
    'BulletedListElement',
    'NumberedListElement',
]