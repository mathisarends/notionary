import re
from dataclasses import dataclass
from enum import StrEnum

from notionary.blocks.enums import BlockType


class AdditionalSyntaxRegistryKey(StrEnum):
    TO_DO_DONE_KEY = "todo_done"
    TOGGLEABLE_HEADING_KEY = "toggleable_heading"
    CAPTION_KEY = "caption"
    SPACE_KEY = "space"
    HEADING_KEY = "heading"


# Special keys for syntax definitions that don't map 1:1 to BlockTypes
# otherwise the BlockType is a good fit
type RegistryKey = BlockType | AdditionalSyntaxRegistryKey


# TODO: Verschiedene Modelle für multi oder inline keys (some fields mutally exclude each others) (some fileds actually dont need a name | im not sure wheter we should definie it here at all)
@dataclass(frozen=True)
class SyntaxDefinition:
    """
    Defines the syntax pattern for a block type.

    Attributes:
        name: The block type this syntax defines
        start_delimiter: The opening delimiter (e.g., "```", "+++", ">")
        end_delimiter: The optional closing delimiter (empty string if none)
        regex_pattern: The compiled regex pattern to match this syntax
        end_regex_pattern: Optional compiled regex pattern for end delimiter
        is_multiline_block: Whether this block can contain child blocks
        is_inline: Whether this is an inline syntax (like [audio](url))
    """

    name: BlockType
    start_delimiter: str
    end_delimiter: str
    regex_pattern: re.Pattern
    end_regex_pattern: re.Pattern | None = None
    is_multiline_block: bool = False
    is_inline: bool = False
