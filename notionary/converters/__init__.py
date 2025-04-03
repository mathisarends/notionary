# Import converters
from .markdown_to_notion_converter import MarkdownToNotionConverter
from .notion_to_markdown_converter import NotionToMarkdownConverter

from .notion_element_registry import ElementRegistry

# Import elements
from .elements.paragraph_element import ParagraphElement
from .elements.headings import HeadingElement
from .elements.callouts import CalloutElement
from .elements.code_blocks import CodeBlockElement
from .elements.dividers import DividerElement
from .elements.tables import TableElement
from .elements.todo_lists import TodoElement
from .elements.lists import BulletedListElement, NumberedListElement
from .elements.quotes import QuoteElement
from .elements.bookmarks import BookmarkElement
from .elements.images import ImageElement

# Register all elements
# Register paragraphs last since they're the fallback
ElementRegistry.register(HeadingElement)
ElementRegistry.register(CalloutElement)
ElementRegistry.register(CodeBlockElement)
ElementRegistry.register(DividerElement)
ElementRegistry.register(TableElement)
ElementRegistry.register(BulletedListElement)
ElementRegistry.register(NumberedListElement)
ElementRegistry.register(QuoteElement)
ElementRegistry.register(TodoElement)
ElementRegistry.register(BookmarkElement)
ElementRegistry.register(ImageElement)
ElementRegistry.register(ParagraphElement)  # Register last!

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