from dataclasses import dataclass


@dataclass(frozen=True)
class MarkdownGrammar:
    spaces_per_nesting_level = 4
    numbered_list_placeholder = "__NUM__"
    column_delimiter = ":::"
    toggle_delimiter = "+++"
    table_delimiter = "|"
