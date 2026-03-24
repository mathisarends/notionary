import re

from notionary.shared.decorators import singleton


@singleton
class MarkdownGrammar:
    def __init__(self) -> None:
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

        # Block Patterns
        self.breadcrumb_pattern = re.compile(r"^\[breadcrumb\]\s*$", re.IGNORECASE)
        self.bulleted_list_pattern = re.compile(r"^(\s*)-\s+(?!\[[ xX]\])(.+)$")
        self.divider_pattern = re.compile(r"^\s*-{3,}\s*$")
        self.numbered_list_pattern = re.compile(r"^(\s*)(\d+)\.\s+(.+)$")
        self.quote_pattern = re.compile(r"^>(?!>)\s*(.+)$")
        self.table_pattern = re.compile(r"^\s*\|(.+)\|\s*$")
        self.table_row_pattern = re.compile(r"^\s*\|([\s\-:|]+)\|\s*$")
        self.table_of_contents_pattern = re.compile(r"^\[toc\]$", re.IGNORECASE)
        self.todo_pattern = re.compile(r"^\s*-\s+\[ \]\s+(.+)$")
        self.todo_done_pattern = re.compile(r"^\s*-\s+\[x\]\s+(.+)$", re.IGNORECASE)
        self.caption_pattern = re.compile(r"^\[caption\]\s+(\S.*)$")
        self.space_pattern = re.compile(r"^\[space\]\s*$")
        self.heading_pattern = re.compile(r"^(#{1,3})[ \t]+(.+)$")
        self.media_end_pattern = re.compile(r"\)")
        self.callout_pattern = re.compile(
            r'\[callout\](?:\(([^"]+?)(?:\s+"([^"]+)")?\)|(?:\s+([^"\n]+?)(?:\s+"([^"]+)")?)(?:\n|$))'
        )
        self.callout_end_pattern = re.compile(r"\)")
        self.code_start_pattern = re.compile(r"^```(\w*)\s*$")
        self.code_end_pattern = re.compile(r"^```\s*$")
        self.column_pattern = re.compile(
            r"^:::\s*column(?:\s+(0?\.\d+|1(?:\.0?)?))??\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        self.column_end_pattern = re.compile(r"^:::\s*$", re.MULTILINE)
        self.column_list_pattern = re.compile(r"^:::\s*columns?\s*$", re.IGNORECASE)
        self.column_list_end_pattern = re.compile(r"^:::\s*$")
        self.equation_start_pattern = re.compile(r"^\$\$\s*$")
        self.equation_end_pattern = re.compile(r"^\$\$\s*$")
        self.toggle_pattern = re.compile(r"^\+\+\+\s+(.+)$")
        self.toggle_end_pattern = re.compile(r"^\+\+\+\s*$")
        self.toggleable_heading_pattern = re.compile(
            r"^\+\+\+\s*(?P<level>#{1,3})(?!#)\s*(.+)$",
            re.IGNORECASE,
        )
        self.toggleable_heading_end_pattern = re.compile(r"^\+\+\+\s*$")
        self.synced_block_pattern = re.compile(r"^>>>\s+(.+)$")

        # Rich Text Patterns
        self.bold_pattern = re.compile(r"\*\*(.+?)\*\*")
        self.italic_pattern = re.compile(r"\*(.+?)\*")
        self.italic_underscore_pattern = re.compile(r"_([^_]+?)_")
        self.underline_pattern = re.compile(r"__(.+?)__")
        self.strikethrough_pattern = re.compile(r"~~(.+?)~~")
        self.inline_code_pattern = re.compile(r"`(.+?)`")
        self.link_pattern = re.compile(r"\[(.+?)\]\((.+?)\)")
        self.inline_equation_pattern = re.compile(r"\$(.+?)\$")
        self.color_pattern = re.compile(r"\((\w+):(.+?)\)")

        # Mention Patterns
        self.page_mention_pattern = self._create_mention_pattern(
            self.page_mention_prefix
        )
        self.database_mention_pattern = self._create_mention_pattern(
            self.database_mention_prefix
        )
        self.datasource_mention_pattern = self._create_mention_pattern(
            self.datasource_mention_prefix
        )
        self.user_mention_pattern = self._create_mention_pattern(
            self.user_mention_prefix
        )
        self.date_mention_pattern = self._create_mention_pattern(
            self.date_mention_prefix
        )

    def _create_mention_pattern(self, prefix: str) -> re.Pattern:
        escaped_prefix = re.escape(prefix)
        escaped_suffix = re.escape(self.mention_suffix)
        return re.compile(rf"{escaped_prefix}([^{escaped_suffix}]+){escaped_suffix}")

    def media_block_pattern(
        self, media_type: str, url_pattern: str | None = None
    ) -> re.Pattern:
        url_pattern = url_pattern or "[^)]+"
        return re.compile(rf"(?<!\!)\[{re.escape(media_type)}\]\(({url_pattern})\)")

    def url_media_block_pattern(self, media_type: str) -> re.Pattern:
        return re.compile(rf"(?<!\!)\[{re.escape(media_type)}\]\((https?://[^\s)]+)\)")
