import re
from dataclasses import dataclass
from enum import StrEnum


class SyntaxDefinitionRegistryKey(StrEnum):
    AUDIO = "audio"
    BOOKMARK = "bookmark"
    IMAGE = "image"
    VIDEO = "video"
    FILE = "file"
    PDF = "pdf"

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

    HEADING = "heading"

    DIVIDER = "divider"
    BREADCRUMB = "breadcrumb"
    TABLE_OF_CONTENTS = "table_of_contents"
    EQUATION = "equation"
    EMBED = "embed"
    TABLE = "table"
    TABLE_ROW = "table_row"

    CAPTION = "caption"
    SPACE = "space"


@dataclass(frozen=True)
class SimpleSyntaxDefinition:
    start_delimiter: str
    regex_pattern: re.Pattern


@dataclass(frozen=True)
class EnclosedSyntaxDefinition:
    start_delimiter: str
    end_delimiter: str
    regex_pattern: re.Pattern
    end_regex_pattern: re.Pattern


type SyntaxDefinition = SimpleSyntaxDefinition | EnclosedSyntaxDefinition
