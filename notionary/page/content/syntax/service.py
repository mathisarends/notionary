import re

from notionary.page.content.syntax.models import SyntaxDefinition, SyntaxRegistryKey


class SyntaxRegistry:
    MULTI_LINE_BLOCK_DELIMITER = ":::"
    TOGGLE_DELIMITER = "+++"
    TABLE_DELIMITER = "|"

    def __init__(self) -> None:
        self._definitions: dict[SyntaxRegistryKey, SyntaxDefinition] = {}
        self._register_defaults()

    def get_audio_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.AUDIO]

    def get_bookmark_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.BOOKMARK]

    def get_breadcrumb_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.BREADCRUMB]

    def get_bulleted_list_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.BULLETED_LIST]

    def get_callout_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.CALLOUT]

    def get_code_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.CODE]

    def get_column_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.COLUMN]

    def get_column_list_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.COLUMN_LIST]

    def get_divider_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.DIVIDER]

    def get_embed_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.EMBED]

    def get_equation_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.EQUATION]

    def get_file_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.FILE]

    def get_image_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.IMAGE]

    def get_numbered_list_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.NUMBERED_LIST]

    def get_pdf_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.PDF]

    def get_quote_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.QUOTE]

    def get_table_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.TABLE]

    def get_table_row_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.TABLE_ROW]

    def get_table_of_contents_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.TABLE_OF_CONTENTS]

    def get_todo_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.TO_DO]

    def get_todo_done_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.TO_DO_DONE]

    def get_toggle_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.TOGGLE]

    def get_toggleable_heading_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.TOGGLEABLE_HEADING]

    def get_video_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.VIDEO]

    def get_caption_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.CAPTION]

    def get_space_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.SPACE]

    def get_heading_syntax(self) -> SyntaxDefinition:
        return self._definitions[SyntaxRegistryKey.HEADING]

    def _register_defaults(self) -> None:
        self._register_audio_syntax()
        self._register_bookmark_syntax()
        self._register_image_syntax()
        self._register_video_syntax()
        self._register_file_syntax()
        self._register_pdf_syntax()

        # List blocks
        self._register_bulleted_list_syntax()
        self._register_numbered_list_syntax()
        self._register_todo_syntax()
        self._register_todo_done_syntax()

        # Container blocks
        self._register_toggle_syntax()
        self._register_toggleable_heading_syntax()
        self._register_callout_syntax()
        self._register_quote_syntax()
        self._register_code_syntax()

        # Column layout blocks
        self._register_column_list_syntax()
        self._register_column_syntax()

        self._register_heading_1_syntax()
        self._register_heading_2_syntax()
        self._register_heading_3_syntax()
        self._register_heading_syntax()  # Shared pattern for regular headings

        self._register_divider_syntax()
        self._register_breadcrumb_syntax()
        self._register_table_of_contents_syntax()
        self._register_equation_syntax()
        self._register_embed_syntax()
        self._register_table_syntax()
        self._register_table_row_syntax()

        # Post-processing and utility blocks
        self._register_caption_syntax()
        self._register_space_syntax()

    def _register_audio_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[audio](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[audio\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[SyntaxRegistryKey.AUDIO] = definition

    def _register_bookmark_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[bookmark](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[bookmark\]\((https?://[^\s\"]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[SyntaxRegistryKey.BOOKMARK] = definition

    def _register_breadcrumb_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[breadcrumb]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[breadcrumb\]\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.BREADCRUMB] = definition

    def _register_bulleted_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="- ",
            end_delimiter="",
            regex_pattern=re.compile(r"^(\s*)-\s+(?!\[[ xX]\])(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.BULLETED_LIST] = definition

    def _register_callout_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter=f"{self.MULTI_LINE_BLOCK_DELIMITER} callout",
            end_delimiter=self.MULTI_LINE_BLOCK_DELIMITER,
            regex_pattern=re.compile(
                rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*callout(?:\s+(\S+))?\s*$", re.IGNORECASE
            ),
            end_regex_pattern=re.compile(rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.CALLOUT] = definition

    def _register_code_syntax(self) -> None:
        code_delimiter = "```"
        definition = SyntaxDefinition(
            start_delimiter=code_delimiter,
            end_delimiter=code_delimiter,
            regex_pattern=re.compile("^" + re.escape(code_delimiter) + r"(\w*)\s*$"),
            end_regex_pattern=re.compile("^" + re.escape(code_delimiter) + r"\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.CODE] = definition

    def _register_column_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter=f"{self.MULTI_LINE_BLOCK_DELIMITER} column",
            end_delimiter=self.MULTI_LINE_BLOCK_DELIMITER,
            regex_pattern=re.compile(
                rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*column(?:\s+(0?\.\d+|1(?:\.0?)?))??\s*$",
                re.IGNORECASE,
            ),
            end_regex_pattern=re.compile(rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.COLUMN] = definition

    def _register_column_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter=f"{self.MULTI_LINE_BLOCK_DELIMITER} columns",
            end_delimiter=self.MULTI_LINE_BLOCK_DELIMITER,
            regex_pattern=re.compile(rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*columns\s*$", re.IGNORECASE),
            end_regex_pattern=re.compile(rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.COLUMN_LIST] = definition

    def _register_divider_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="---",
            end_delimiter="",
            regex_pattern=re.compile(r"^-{3,}\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.DIVIDER] = definition

    def _register_embed_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[embed](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[embed\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[SyntaxRegistryKey.EMBED] = definition

    def _register_equation_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="$$",
            end_delimiter="$$",
            regex_pattern=re.compile(r"^\$\$\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.EQUATION] = definition

    def _register_file_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[file](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[file\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[SyntaxRegistryKey.FILE] = definition

    def _register_heading_1_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="# ",
            end_delimiter="",
            regex_pattern=re.compile(r"^#\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.HEADING_1] = definition

    def _register_heading_2_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="## ",
            end_delimiter="",
            regex_pattern=re.compile(r"^#{2}\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.HEADING_2] = definition

    def _register_heading_3_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="### ",
            end_delimiter="",
            regex_pattern=re.compile(r"^#{3}\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.HEADING_3] = definition

    def _register_toggleable_heading_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="+++ #",
            end_delimiter="+++",
            regex_pattern=re.compile(r"^[+]{3}\s*(?P<level>#{1,3})(?!#)\s*(.+)$", re.IGNORECASE),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TOGGLE] = definition

    def _register_image_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[image](",
            end_delimiter=")",
            regex_pattern=re.compile(r"(?<!!)\[image\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[SyntaxRegistryKey.IMAGE] = definition

    def _register_numbered_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="1. ",
            end_delimiter="",
            regex_pattern=re.compile(r"^(\s*)(\d+)\.\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.NUMBERED_LIST] = definition

    def _register_pdf_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[pdf](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[pdf\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[SyntaxRegistryKey.PDF] = definition

    def _register_quote_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="> ",
            end_delimiter="",
            regex_pattern=re.compile(r"^>(?!>)\s*(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.QUOTE] = definition

    def _register_table_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter=self.TABLE_DELIMITER,
            end_delimiter="",
            regex_pattern=re.compile(
                rf"^\s*{re.escape(self.TABLE_DELIMITER)}(.+){re.escape(self.TABLE_DELIMITER)}\s*$"
            ),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TABLE] = definition

    def _register_table_row_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter=self.TABLE_DELIMITER,
            end_delimiter="",
            regex_pattern=re.compile(
                rf"^\s*{re.escape(self.TABLE_DELIMITER)}([\s\-:|]+){re.escape(self.TABLE_DELIMITER)}\s*$"
            ),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TABLE_ROW] = definition

    def _register_table_of_contents_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[toc]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[toc\]\s*$", re.IGNORECASE),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TABLE_OF_CONTENTS] = definition

    def _register_todo_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="- [ ]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\s*-\s+\[ \]\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TO_DO] = definition

    def _register_todo_done_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="- [x]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\s*-\s+\[x\]\s+(.+)$", re.IGNORECASE),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TO_DO_DONE] = definition

    def _register_toggle_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter=self.TOGGLE_DELIMITER,
            end_delimiter=self.TOGGLE_DELIMITER,
            regex_pattern=re.compile(rf"^{re.escape(self.TOGGLE_DELIMITER)}\s+(.+)$"),
            end_regex_pattern=re.compile(rf"^{re.escape(self.TOGGLE_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TOGGLE] = definition

    def _register_toggleable_heading_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter=f"{self.TOGGLE_DELIMITER} #",
            end_delimiter=self.TOGGLE_DELIMITER,
            regex_pattern=re.compile(
                rf"^{re.escape(self.TOGGLE_DELIMITER)}\s*(?P<level>#{1, 3})(?!#)\s*(.+)$", re.IGNORECASE
            ),
            end_regex_pattern=re.compile(rf"^{re.escape(self.TOGGLE_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.TOGGLEABLE_HEADING] = definition

    def _register_video_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[video](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[video\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[SyntaxRegistryKey.VIDEO] = definition

    def _register_caption_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[caption]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[caption\]\s+(\S.*)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.CAPTION] = definition

    def _register_space_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[space]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[space\]\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.SPACE] = definition

    def _register_heading_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="#",
            end_delimiter="",
            regex_pattern=re.compile(r"^(#{1,3})[ \t]+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[SyntaxRegistryKey.HEADING] = definition
