import re
from functools import cached_property


class MarkdownGrammar:
    _instance: "MarkdownGrammar | None" = None

    def __new__(cls) -> "MarkdownGrammar":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Configuration
        self.spaces_per_nesting_level = 4
        self.numbered_list_placeholder = "__NUM__"

        # Delimiters
        self.breadcrumb_delimiter = "[breadcrumb]"
        self.bulleted_list_delimiter = "- "
        self.divider_delimiter = "---"
        self.numbered_list_delimiter = "1. "
        self.quote_delimiter = "> "
        self.table_delimiter = "|"
        self.table_of_contents_delimiter = "[toc]"
        self.todo_delimiter = "- [ ]"
        self.todo_done_delimiter = "- [x]"
        self.caption_delimiter = "[caption]"
        self.space_delimiter = "[space]"
        self.heading_delimiter = "#"
        self.column_delimiter = ":::"
        self.toggle_delimiter = "+++"
        self.code_delimiter = "```"
        self.equation_delimiter = "$$"
        self.callout_delimiter = "[callout]"
        self.media_end_delimiter = ")"
        self.synced_block_delimiter = ">>>"

        # Mention Delimiters
        self.page_mention_prefix = "@page["
        self.database_mention_prefix = "@database["
        self.datasource_mention_prefix = "@datasource["
        self.user_mention_prefix = "@user["
        self.date_mention_prefix = "@date["
        self.mention_suffix = "]"

        # Rich Text Formatting
        self.link_prefix = "["
        self.link_middle = "]("
        self.link_suffix = ")"
        self.code_wrapper = "`"
        self.strikethrough_wrapper = "~~"
        self.italic_wrapper = "*"
        self.underline_wrapper = "__"
        self.bold_wrapper = "**"
        self.color_prefix = "=={"
        self.color_middle = "}"
        self.color_suffix = "=="
        self.inline_equation_wrapper = "$"
        self.background_color_wrapper = "=="

    def _create_mention_pattern(self, prefix: str) -> re.Pattern:
        escaped_prefix = re.escape(prefix)
        escaped_suffix = re.escape(self.mention_suffix)
        return re.compile(rf"{escaped_prefix}([^{escaped_suffix}]+){escaped_suffix}")

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
            r'\[callout\](?:\(([^"]+?)(?:\s+"([^"]+)")?\)|(?:\s+([^"\n]+?)(?:\s+"([^"]+)")?)(?:\n|$))'
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

    @cached_property
    def bold_pattern(self) -> re.Pattern:
        return re.compile(r"\*\*(.+?)\*\*")

    @cached_property
    def italic_pattern(self) -> re.Pattern:
        return re.compile(r"\*(.+?)\*")

    @cached_property
    def italic_underscore_pattern(self) -> re.Pattern:
        return re.compile(r"_([^_]+?)_")

    @cached_property
    def underline_pattern(self) -> re.Pattern:
        return re.compile(r"__(.+?)__")

    @cached_property
    def strikethrough_pattern(self) -> re.Pattern:
        return re.compile(r"~~(.+?)~~")

    @cached_property
    def inline_code_pattern(self) -> re.Pattern:
        return re.compile(r"`(.+?)`")

    @cached_property
    def link_pattern(self) -> re.Pattern:
        return re.compile(r"\[(.+?)\]\((.+?)\)")

    @cached_property
    def inline_equation_pattern(self) -> re.Pattern:
        return re.compile(r"\$(.+?)\$")

    @cached_property
    def color_pattern(self) -> re.Pattern:
        return re.compile(r"\((\w+):(.+?)\)")

    @cached_property
    def page_mention_pattern(self) -> re.Pattern:
        return self._create_mention_pattern(self.page_mention_prefix)

    @cached_property
    def database_mention_pattern(self) -> re.Pattern:
        return self._create_mention_pattern(self.database_mention_prefix)

    @cached_property
    def datasource_mention_pattern(self) -> re.Pattern:
        return self._create_mention_pattern(self.datasource_mention_prefix)

    @cached_property
    def user_mention_pattern(self) -> re.Pattern:
        return self._create_mention_pattern(self.user_mention_prefix)

    @cached_property
    def date_mention_pattern(self) -> re.Pattern:
        return self._create_mention_pattern(self.date_mention_prefix)

    @cached_property
    def synced_block_pattern(self) -> re.Pattern:
        return re.compile(r"^>>>\s+(.+)$")
