import re
from functools import cached_property

from notionary.utils.decorators import singleton


@singleton
class MarkdownGrammar:
    def __init__(self) -> None:
        # Configuration
        self._spaces_per_nesting_level = 4
        self._numbered_list_placeholder = "__NUM__"

        # Delimiters
        self._breadcrumb_delimiter = "[breadcrumb]"
        self._bulleted_list_delimiter = "- "
        self._divider_delimiter = "---"
        self._numbered_list_delimiter = "1. "
        self._quote_delimiter = "> "
        self._table_delimiter = "|"
        self._table_of_contents_delimiter = "[toc]"
        self._todo_delimiter = "- [ ]"
        self._todo_done_delimiter = "- [x]"
        self._caption_delimiter = "[caption]"
        self._space_delimiter = "[space]"
        self._heading_delimiter = "#"
        self._column_delimiter = ":::"
        self._toggle_delimiter = "+++"
        self._code_delimiter = "```"
        self._equation_delimiter = "$$"
        self._callout_delimiter = "[callout]"
        self._media_end_delimiter = ")"

        # Mention Delimiters
        self._page_mention_prefix = "@page["
        self._database_mention_prefix = "@database["
        self._datasource_mention_prefix = "@datasource["
        self._user_mention_prefix = "@user["
        self._date_mention_prefix = "@date["
        self._mention_suffix = "]"

        # Rich Text Formatting
        self._link_prefix = "["
        self._link_middle = "]("
        self._link_suffix = ")"
        self._code_wrapper = "`"
        self._strikethrough_wrapper = "~~"
        self._italic_wrapper = "*"
        self._underline_wrapper = "__"
        self._bold_wrapper = "**"
        self._color_prefix = "=={"
        self._color_middle = "}"
        self._color_suffix = "=="
        self._inline_equation_wrapper = "$"

    @property
    def spaces_per_nesting_level(self) -> int:
        return self._spaces_per_nesting_level

    @property
    def numbered_list_placeholder(self) -> str:
        return self._numbered_list_placeholder

    @property
    def breadcrumb_delimiter(self) -> str:
        return self._breadcrumb_delimiter

    @property
    def bulleted_list_delimiter(self) -> str:
        return self._bulleted_list_delimiter

    @property
    def divider_delimiter(self) -> str:
        return self._divider_delimiter

    @property
    def numbered_list_delimiter(self) -> str:
        return self._numbered_list_delimiter

    @property
    def quote_delimiter(self) -> str:
        return self._quote_delimiter

    @property
    def table_delimiter(self) -> str:
        return self._table_delimiter

    @property
    def table_of_contents_delimiter(self) -> str:
        return self._table_of_contents_delimiter

    @property
    def todo_delimiter(self) -> str:
        return self._todo_delimiter

    @property
    def todo_done_delimiter(self) -> str:
        return self._todo_done_delimiter

    @property
    def caption_delimiter(self) -> str:
        return self._caption_delimiter

    @property
    def space_delimiter(self) -> str:
        return self._space_delimiter

    @property
    def heading_delimiter(self) -> str:
        return self._heading_delimiter

    @property
    def column_delimiter(self) -> str:
        return self._column_delimiter

    @property
    def toggle_delimiter(self) -> str:
        return self._toggle_delimiter

    @property
    def code_delimiter(self) -> str:
        return self._code_delimiter

    @property
    def equation_delimiter(self) -> str:
        return self._equation_delimiter

    @property
    def callout_delimiter(self) -> str:
        return self._callout_delimiter

    @property
    def media_end_delimiter(self) -> str:
        return self._media_end_delimiter

    @property
    def page_mention_prefix(self) -> str:
        return self._page_mention_prefix

    @property
    def database_mention_prefix(self) -> str:
        return self._database_mention_prefix

    @property
    def datasource_mention_prefix(self) -> str:
        return self._datasource_mention_prefix

    @property
    def user_mention_prefix(self) -> str:
        return self._user_mention_prefix

    @property
    def date_mention_prefix(self) -> str:
        return self._date_mention_prefix

    @property
    def mention_suffix(self) -> str:
        return self._mention_suffix

    @property
    def link_prefix(self) -> str:
        return self._link_prefix

    @property
    def link_middle(self) -> str:
        return self._link_middle

    @property
    def link_suffix(self) -> str:
        return self._link_suffix

    @property
    def code_wrapper(self) -> str:
        return self._code_wrapper

    @property
    def strikethrough_wrapper(self) -> str:
        return self._strikethrough_wrapper

    @property
    def italic_wrapper(self) -> str:
        return self._italic_wrapper

    @property
    def underline_wrapper(self) -> str:
        return self._underline_wrapper

    @property
    def bold_wrapper(self) -> str:
        return self._bold_wrapper

    @property
    def color_prefix(self) -> str:
        return self._color_prefix

    @property
    def color_middle(self) -> str:
        return self._color_middle

    @property
    def color_suffix(self) -> str:
        return self._color_suffix

    @property
    def inline_equation_wrapper(self) -> str:
        return self._inline_equation_wrapper

    # Pattern Definitions
    @cached_property
    def breadcrumb_pattern(self) -> re.Pattern:
        return re.compile(r"^\[breadcrumb\]\s*$", re.IGNORECASE)

    @cached_property
    def bulleted_list_pattern(self) -> re.Pattern:
        return re.compile(r"^(\s*)-\s+(?!\[[ xX]\])(.+)$")

    @cached_property
    def divider_pattern(self) -> re.Pattern:
        return re.compile(r"^\s*-{3,}\s*$")

    @cached_property
    def numbered_list_pattern(self) -> re.Pattern:
        return re.compile(r"^(\s*)(\d+)\.\s+(.+)$")

    @cached_property
    def quote_pattern(self) -> re.Pattern:
        return re.compile(r"^>(?!>)\s*(.+)$")

    @cached_property
    def table_pattern(self) -> re.Pattern:
        delimiter = re.escape(self.table_delimiter)
        return re.compile(rf"^\s*{delimiter}(.+){delimiter}\s*$")

    @cached_property
    def table_row_pattern(self) -> re.Pattern:
        delimiter = re.escape(self.table_delimiter)
        return re.compile(rf"^\s*{delimiter}([\s\-:|]+){delimiter}\s*$")

    @cached_property
    def table_of_contents_pattern(self) -> re.Pattern:
        return re.compile(r"^\[toc\]$", re.IGNORECASE)

    @cached_property
    def todo_pattern(self) -> re.Pattern:
        return re.compile(r"^\s*-\s+\[ \]\s+(.+)$")

    @cached_property
    def todo_done_pattern(self) -> re.Pattern:
        return re.compile(r"^\s*-\s+\[x\]\s+(.+)$", re.IGNORECASE)

    @cached_property
    def caption_pattern(self) -> re.Pattern:
        return re.compile(r"^\[caption\]\s+(\S.*)$")

    @cached_property
    def space_pattern(self) -> re.Pattern:
        return re.compile(r"^\[space\]\s*$")

    @property
    def heading_pattern(self) -> re.Pattern:
        return re.compile(r"^(#{1,3})[ \t]+(.+)$")

    def media_block_pattern(
        self, media_type: str, url_pattern: str | None = None
    ) -> re.Pattern:
        url_pattern = url_pattern or "[^)]+"
        return re.compile(rf"(?<!\!)\[{re.escape(media_type)}\]\(({url_pattern})\)")

    def url_media_block_pattern(self, media_type: str) -> re.Pattern:
        return re.compile(rf"(?<!\!)\[{re.escape(media_type)}\]\((https?://[^\s)]+)\)")

    @cached_property
    def media_end_pattern(self) -> re.Pattern:
        return re.compile(r"\)")

    @cached_property
    def callout_pattern(self) -> re.Pattern:
        return re.compile(
            r'\[callout\](?:\(([^")]+?)(?:\s+"([^"]+)")?\)|(?:\s+([^"\n]+?)(?:\s+"([^"]+)")?)(?:\n|$))'
        )

    @cached_property
    def callout_end_pattern(self) -> re.Pattern:
        return re.compile(r"\)")

    @cached_property
    def code_start_pattern(self) -> re.Pattern:
        return re.compile("^" + re.escape(self.code_delimiter) + r"(\w*)\s*$")

    @cached_property
    def code_end_pattern(self) -> re.Pattern:
        return re.compile("^" + re.escape(self.code_delimiter) + r"\s*$")

    @cached_property
    def column_pattern(self) -> re.Pattern:
        delimiter = re.escape(self.column_delimiter)
        return re.compile(
            rf"^{delimiter}\s*column(?:\s+(0?\.\d+|1(?:\.0?)?))??\s*$",
            re.IGNORECASE | re.MULTILINE,
        )

    @cached_property
    def column_end_pattern(self) -> re.Pattern:
        return re.compile(rf"^{re.escape(self.column_delimiter)}\s*$", re.MULTILINE)

    @cached_property
    def column_list_pattern(self) -> re.Pattern:
        return re.compile(
            rf"^{re.escape(self.column_delimiter)}\s*columns?\s*$", re.IGNORECASE
        )

    @cached_property
    def column_list_end_pattern(self) -> re.Pattern:
        return re.compile(rf"^{re.escape(self.column_delimiter)}\s*$")

    @cached_property
    def equation_start_pattern(self) -> re.Pattern:
        return re.compile(r"^\$\$\s*$")

    @cached_property
    def equation_end_pattern(self) -> re.Pattern:
        return re.compile(r"^\$\$\s*$")

    @cached_property
    def toggle_pattern(self) -> re.Pattern:
        return re.compile(rf"^{re.escape(self.toggle_delimiter)}\s+(.+)$")

    @cached_property
    def toggle_end_pattern(self) -> re.Pattern:
        return re.compile(rf"^{re.escape(self.toggle_delimiter)}\s*$")

    @cached_property
    def toggleable_heading_pattern(self) -> re.Pattern:
        escaped_delimiter = re.escape(self.toggle_delimiter)
        return re.compile(
            rf"^{escaped_delimiter}\s*(?P<level>#{{1,3}})(?!#)\s*(.+)$",
            re.IGNORECASE,
        )

    @cached_property
    def toggleable_heading_end_pattern(self) -> re.Pattern:
        return re.compile(rf"^{re.escape(self.toggle_delimiter)}\s*$")
