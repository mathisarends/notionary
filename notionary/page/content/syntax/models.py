import re
from dataclasses import dataclass
from enum import StrEnum


class SyntaxRegistryKey(StrEnum):
    AUDIO = "audio"
    BOOKMARK = "bookmark"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    PDF = "pdf"

    # List blocks
    BULLETED_LIST = "bulleted_list"
    NUMBERED_LIST = "numbered_list"
    TO_DO = "todo"
    TO_DO_DONE = "todo_done"

    TOGGLE = "toggle"
    TOGGLEABLE_HEADING = "toggleable_heading"
    CALLOUT = "callout"
    QUOTE = "quote"
    CODE = "code"

    COLUMN_LIST = "column_list"
    COLUMN = "column"

    # Heading blocks
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    HEADING = "heading"  # Shared pattern for regular headings

    DIVIDER = "divider"
    BREADCRUMB = "breadcrumb"
    TABLE_OF_CONTENTS = "table_of_contents"
    EQUATION = "equation"
    EMBED = "embed"
    TABLE = "table"
    TABLE_ROW = "table_row"

    CAPTION = "caption"
    SPACE = "space"


# some elemente need closing delimiters, others not
# either use union type or validate config in service
@dataclass(frozen=True)
class SyntaxDefinition:
    """
    Defines the syntax pattern for a block type.

    Attributes:
        start_delimiter: The opening delimiter (e.g., "```", "+++", ">")
        end_delimiter: The optional closing delimiter (empty string if none)
        regex_pattern: The compiled regex pattern to match this syntax
        end_regex_pattern: Optional compiled regex pattern for end delimiter
        is_multiline_block: Whether this block can contain child blocks
        is_inline: Whether this is an inline syntax (like [audio](url))
    """

    start_delimiter: str
    end_delimiter: str
    regex_pattern: re.Pattern
    end_regex_pattern: re.Pattern | None = None
