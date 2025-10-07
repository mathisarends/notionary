import re

from notionary.blocks.enums import BlockType
from notionary.page.content.syntax.models import AdditionalSyntaxRegistryKey, RegistryKey, SyntaxDefinition


class SyntaxRegistry:
    MULTI_LINE_BLOCK_DELIMITER = ":::"
    TOGGLE_DELIMITER = "+++"
    TABLE_DELIMITER = "|"

    def __init__(self) -> None:
        self._definitions: dict[RegistryKey, SyntaxDefinition] = {}
        self._register_defaults()

    def get_audio_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.AUDIO]

    def get_bookmark_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.BOOKMARK]

    def get_breadcrumb_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.BREADCRUMB]

    def get_bulleted_list_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.BULLETED_LIST_ITEM]

    def get_callout_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.CALLOUT]

    def get_code_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.CODE]

    def get_column_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.COLUMN]

    def get_column_list_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.COLUMN_LIST]

    def get_divider_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.DIVIDER]

    def get_embed_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.EMBED]

    def get_equation_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.EQUATION]

    def get_file_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.FILE]

    def get_image_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.IMAGE]

    def get_numbered_list_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.NUMBERED_LIST_ITEM]

    def get_pdf_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.PDF]

    def get_quote_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.QUOTE]

    def get_table_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.TABLE]

    def get_table_row_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.TABLE_ROW]

    def get_table_of_contents_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.TABLE_OF_CONTENTS]

    def get_todo_syntax(self) -> SyntaxDefinition:
        """Returns syntax for unchecked todos: - [ ] item"""
        return self._definitions[BlockType.TO_DO]

    def get_todo_done_syntax(self) -> SyntaxDefinition:
        """Returns syntax for checked todos: - [x] item"""
        return self._definitions[AdditionalSyntaxRegistryKey.TO_DO_DONE_KEY]

    def get_toggle_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.TOGGLE]

    def get_toggleable_heading_syntax(self) -> SyntaxDefinition:
        """Returns syntax for toggleable headings: +++ # Title"""
        return self._definitions[AdditionalSyntaxRegistryKey.TOGGLEABLE_HEADING_KEY]

    def get_video_syntax(self) -> SyntaxDefinition:
        return self._definitions[BlockType.VIDEO]

    def get_caption_syntax(self) -> SyntaxDefinition:
        """Returns syntax for [caption] text"""
        return self._definitions[AdditionalSyntaxRegistryKey.CAPTION_KEY]

    def get_space_syntax(self) -> SyntaxDefinition:
        """Returns syntax for [space] markers"""
        return self._definitions[AdditionalSyntaxRegistryKey.SPACE_KEY]

    def get_heading_syntax(self) -> SyntaxDefinition:
        """Returns syntax for regular headings: #, ##, ###"""
        return self._definitions[AdditionalSyntaxRegistryKey.HEADING_KEY]

    def _register_defaults(self) -> None:
        # Inline file/media blocks
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
        self._register_todo_done_syntax()  # Separate syntax for checked todos

        # Container blocks
        self._register_toggle_syntax()
        self._register_toggleable_heading_syntax()  # Separate from toggle
        self._register_callout_syntax()
        self._register_quote_syntax()
        self._register_code_syntax()

        # Column layout blocks
        self._register_column_list_syntax()
        self._register_column_syntax()

        # Heading blocks (Note: HeadingParser doesn't use registry - uses shared pattern)
        self._register_heading_1_syntax()
        self._register_heading_2_syntax()
        self._register_heading_3_syntax()
        self._register_heading_syntax()  # Shared pattern for regular headings

        # Special blocks
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
            name=BlockType.AUDIO,
            start_delimiter="[audio](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[audio\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[definition.name] = definition

    def _register_bookmark_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.BOOKMARK,
            start_delimiter="[bookmark](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[bookmark\]\((https?://[^\s\"]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[definition.name] = definition

    def _register_breadcrumb_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.BREADCRUMB,
            start_delimiter="[breadcrumb]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[breadcrumb\]\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_bulleted_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.BULLETED_LIST_ITEM,
            start_delimiter="- ",
            end_delimiter="",
            regex_pattern=re.compile(r"^(\s*)-\s+(?!\[[ xX]\])(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_callout_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.CALLOUT,
            start_delimiter=f"{self.MULTI_LINE_BLOCK_DELIMITER} callout",
            end_delimiter=self.MULTI_LINE_BLOCK_DELIMITER,
            regex_pattern=re.compile(
                rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*callout(?:\s+(\S+))?\s*$", re.IGNORECASE
            ),
            end_regex_pattern=re.compile(rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_code_syntax(self) -> None:
        code_delimiter = "```"
        definition = SyntaxDefinition(
            name=BlockType.CODE,
            start_delimiter=code_delimiter,
            end_delimiter=code_delimiter,
            regex_pattern=re.compile("^" + re.escape(code_delimiter) + r"(\w*)\s*$"),
            end_regex_pattern=re.compile("^" + re.escape(code_delimiter) + r"\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_column_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.COLUMN,
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
        self._definitions[definition.name] = definition

    def _register_column_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.COLUMN_LIST,
            start_delimiter=f"{self.MULTI_LINE_BLOCK_DELIMITER} columns",
            end_delimiter=self.MULTI_LINE_BLOCK_DELIMITER,
            regex_pattern=re.compile(rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*columns\s*$", re.IGNORECASE),
            end_regex_pattern=re.compile(rf"^{re.escape(self.MULTI_LINE_BLOCK_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_divider_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.DIVIDER,
            start_delimiter="---",
            end_delimiter="",
            regex_pattern=re.compile(r"^-{3,}\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_embed_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.EMBED,
            start_delimiter="[embed](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[embed\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[definition.name] = definition

    def _register_equation_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.EQUATION,
            start_delimiter="$$",
            end_delimiter="$$",
            regex_pattern=re.compile(r"^\$\$\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_file_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.FILE,
            start_delimiter="[file](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[file\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[definition.name] = definition

    def _register_heading_1_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.HEADING_1,
            start_delimiter="# ",
            end_delimiter="",
            regex_pattern=re.compile(r"^#\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_heading_2_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.HEADING_2,
            start_delimiter="## ",
            end_delimiter="",
            regex_pattern=re.compile(r"^#{2}\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_heading_3_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.HEADING_3,
            start_delimiter="### ",
            end_delimiter="",
            regex_pattern=re.compile(r"^#{3}\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_toggleable_heading_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.TOGGLE,  # Reuses TOGGLE for toggleable headings
            start_delimiter="+++ #",
            end_delimiter="+++",
            regex_pattern=re.compile(r"^[+]{3}\s*(?P<level>#{1,3})(?!#)\s*(.+)$", re.IGNORECASE),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_image_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.IMAGE,
            start_delimiter="[image](",
            end_delimiter=")",
            regex_pattern=re.compile(r"(?<!!)\[image\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[definition.name] = definition

    def _register_numbered_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.NUMBERED_LIST_ITEM,
            start_delimiter="1. ",
            end_delimiter="",
            regex_pattern=re.compile(r"^(\s*)(\d+)\.\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_pdf_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.PDF,
            start_delimiter="[pdf](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[pdf\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[definition.name] = definition

    def _register_quote_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.QUOTE,
            start_delimiter="> ",
            end_delimiter="",
            regex_pattern=re.compile(r"^>(?!>)\s*(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_table_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.TABLE,
            start_delimiter=self.TABLE_DELIMITER,
            end_delimiter="",
            regex_pattern=re.compile(
                rf"^\s*{re.escape(self.TABLE_DELIMITER)}(.+){re.escape(self.TABLE_DELIMITER)}\s*$"
            ),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_table_row_syntax(self) -> None:
        """Register syntax for table separator rows (e.g., |---|---|)"""
        definition = SyntaxDefinition(
            name=BlockType.TABLE_ROW,
            start_delimiter=self.TABLE_DELIMITER,
            end_delimiter="",
            regex_pattern=re.compile(
                rf"^\s*{re.escape(self.TABLE_DELIMITER)}([\s\-:|]+){re.escape(self.TABLE_DELIMITER)}\s*$"
            ),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_table_of_contents_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.TABLE_OF_CONTENTS,
            start_delimiter="[toc]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[toc\]\s*$", re.IGNORECASE),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_todo_syntax(self) -> None:
        """Register syntax for unchecked todos: - [ ] item"""
        definition = SyntaxDefinition(
            name=BlockType.TO_DO,
            start_delimiter="- [ ]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\s*-\s+\[ \]\s+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_todo_done_syntax(self) -> None:
        """Register syntax for checked todos: - [x] item"""
        definition = SyntaxDefinition(
            name=BlockType.TO_DO,
            start_delimiter="- [x]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\s*-\s+\[x\]\s+(.+)$", re.IGNORECASE),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[AdditionalSyntaxRegistryKey.TO_DO_DONE_KEY] = definition

    def _register_toggle_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.TOGGLE,
            start_delimiter=self.TOGGLE_DELIMITER,
            end_delimiter=self.TOGGLE_DELIMITER,
            regex_pattern=re.compile(rf"^{re.escape(self.TOGGLE_DELIMITER)}\s+(.+)$"),
            end_regex_pattern=re.compile(rf"^{re.escape(self.TOGGLE_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[definition.name] = definition

    def _register_toggleable_heading_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.TOGGLE,
            start_delimiter=f"{self.TOGGLE_DELIMITER} #",
            end_delimiter=self.TOGGLE_DELIMITER,
            regex_pattern=re.compile(
                rf"^{re.escape(self.TOGGLE_DELIMITER)}\s*(?P<level>#{1, 3})(?!#)\s*(.+)$", re.IGNORECASE
            ),
            end_regex_pattern=re.compile(rf"^{re.escape(self.TOGGLE_DELIMITER)}\s*$"),
            is_multiline_block=True,
            is_inline=False,
        )
        self._definitions[AdditionalSyntaxRegistryKey.TOGGLEABLE_HEADING_KEY] = definition

    def _register_video_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.VIDEO,
            start_delimiter="[video](",
            end_delimiter=")",
            regex_pattern=re.compile(r"\[video\]\(([^)]+)\)"),
            is_multiline_block=False,
            is_inline=True,
        )
        self._definitions[definition.name] = definition

    def _register_caption_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.PARAGRAPH,  # Captions modify existing blocks, not a standalone type
            start_delimiter="[caption]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[caption\]\s+(\S.*)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[AdditionalSyntaxRegistryKey.CAPTION_KEY] = definition

    def _register_space_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.PARAGRAPH,
            start_delimiter="[space]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[space\]\s*$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[AdditionalSyntaxRegistryKey.SPACE_KEY] = definition

    def _register_heading_syntax(self) -> None:
        definition = SyntaxDefinition(
            name=BlockType.HEADING_1,
            start_delimiter="#",
            end_delimiter="",
            regex_pattern=re.compile(r"^(#{1,3})[ \t]+(.+)$"),
            is_multiline_block=False,
            is_inline=False,
        )
        self._definitions[AdditionalSyntaxRegistryKey.HEADING_KEY] = definition
