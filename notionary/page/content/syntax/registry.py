import re

from notionary.page.content.syntax.grammar import MarkdownGrammar
from notionary.page.content.syntax.models import SyntaxDefinition, SyntaxRegistryKey


# TODO: Add support for file upload in blocks for file types (refactor file types aswell)
# differentiate between external and uploaded files (file like blocks)
class SyntaxRegistry:
    def __init__(self, markdown_markdown_grammar: MarkdownGrammar | None = None) -> None:
        self._markdown_grammar = markdown_markdown_grammar or MarkdownGrammar()

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

    def _create_media_syntax(self, media_type: str, url_pattern: str | None = None) -> SyntaxDefinition:
        url_pattern = url_pattern or "[^)]+"
        return SyntaxDefinition(
            start_delimiter=f"[{media_type}](",
            end_delimiter=")",
            regex_pattern=re.compile(rf"(?<!\!)\[{re.escape(media_type)}\]\(({url_pattern})\)"),
        )

    def _create_url_media_syntax(self, media_type: str) -> SyntaxDefinition:
        return SyntaxDefinition(
            start_delimiter=f"[{media_type}](",
            end_delimiter=")",
            regex_pattern=re.compile(rf"(?<!\!)\[{re.escape(media_type)}\]\((https?://[^\s)]+)\)"),
        )

    def _register_defaults(self) -> None:
        self._register_audio_syntax()
        self._register_video_syntax()
        self._register_image_syntax()
        self._register_file_syntax()
        self._register_pdf_syntax()
        self._register_bookmark_syntax()
        self._register_embed_syntax()

        self._register_bulleted_list_syntax()
        self._register_numbered_list_syntax()
        self._register_todo_syntax()
        self._register_todo_done_syntax()

        self._register_toggle_syntax()
        self._register_toggleable_heading_syntax()
        self._register_callout_syntax()
        self._register_quote_syntax()
        self._register_code_syntax()

        self._register_column_list_syntax()
        self._register_column_syntax()

        self._register_heading_syntax()

        self._register_divider_syntax()
        self._register_breadcrumb_syntax()
        self._register_table_of_contents_syntax()
        self._register_equation_syntax()
        self._register_table_syntax()
        self._register_table_row_syntax()

        self._register_caption_syntax()
        self._register_space_syntax()

    def _register_audio_syntax(self) -> None:
        self._definitions[SyntaxRegistryKey.AUDIO] = self._create_media_syntax("audio")

    def _register_video_syntax(self) -> None:
        self._definitions[SyntaxRegistryKey.VIDEO] = self._create_media_syntax("video")

    def _register_image_syntax(self) -> None:
        self._definitions[SyntaxRegistryKey.IMAGE] = self._create_media_syntax("image")

    def _register_file_syntax(self) -> None:
        self._definitions[SyntaxRegistryKey.FILE] = self._create_media_syntax("file")

    def _register_pdf_syntax(self) -> None:
        self._definitions[SyntaxRegistryKey.PDF] = self._create_media_syntax("pdf")

    def _register_bookmark_syntax(self) -> None:
        self._definitions[SyntaxRegistryKey.BOOKMARK] = self._create_url_media_syntax("bookmark")

    def _register_embed_syntax(self) -> None:
        self._definitions[SyntaxRegistryKey.EMBED] = self._create_url_media_syntax("embed")

    def _register_breadcrumb_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[breadcrumb]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[breadcrumb\]\s*$", re.IGNORECASE),
        )
        self._definitions[SyntaxRegistryKey.BREADCRUMB] = definition

    def _register_bulleted_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="- ",
            end_delimiter="",
            regex_pattern=re.compile(r"^(\s*)-\s+(?!\[[ xX]\])(.+)$"),
        )
        self._definitions[SyntaxRegistryKey.BULLETED_LIST] = definition

    def _register_callout_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[callout]",
            end_delimiter=")",
            regex_pattern=re.compile(
                r'\[callout\](?:\(([^")]+?)(?:\s+"([^"]+)")?\)|(?:\s+([^"\n]+?)(?:\s+"([^"]+)")?)(?:\n|$))'
            ),
        )
        self._definitions[SyntaxRegistryKey.CALLOUT] = definition

    def _register_code_syntax(self) -> None:
        code_delimiter = "```"
        definition = SyntaxDefinition(
            start_delimiter=code_delimiter,
            end_delimiter=code_delimiter,
            regex_pattern=re.compile("^" + re.escape(code_delimiter) + r"(\w*)\s*$"),
            end_regex_pattern=re.compile("^" + re.escape(code_delimiter) + r"\s*$"),
        )
        self._definitions[SyntaxRegistryKey.CODE] = definition

    def _register_column_syntax(self) -> None:
        delimiter = self._markdown_grammar.column_delimiter
        definition = SyntaxDefinition(
            start_delimiter=f"{delimiter} column",
            end_delimiter=delimiter,
            regex_pattern=re.compile(
                rf"^{re.escape(delimiter)}\s*column(?:\s+(0?\.\d+|1(?:\.0?)?))??\s*$",
                re.IGNORECASE | re.MULTILINE,
            ),
            end_regex_pattern=re.compile(rf"^{re.escape(delimiter)}\s*$", re.MULTILINE),
        )
        self._definitions[SyntaxRegistryKey.COLUMN] = definition

    def _register_column_list_syntax(self) -> None:
        delimiter = self._markdown_grammar.column_delimiter
        definition = SyntaxDefinition(
            start_delimiter=f"{delimiter} columns",
            end_delimiter=delimiter,
            regex_pattern=re.compile(rf"^{re.escape(delimiter)}\s*columns?\s*$", re.IGNORECASE),
            end_regex_pattern=re.compile(rf"^{re.escape(delimiter)}\s*$"),
        )
        self._definitions[SyntaxRegistryKey.COLUMN_LIST] = definition

    def _register_divider_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="---",
            end_delimiter="",
            regex_pattern=re.compile(r"^\s*-{3,}\s*$"),
        )
        self._definitions[SyntaxRegistryKey.DIVIDER] = definition

    def _register_equation_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="$$",
            end_delimiter="$$",
            regex_pattern=re.compile(r"^\$\$\s*$"),
        )
        self._definitions[SyntaxRegistryKey.EQUATION] = definition

    def _register_numbered_list_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="1. ",
            end_delimiter="",
            regex_pattern=re.compile(r"^(\s*)(\d+)\.\s+(.+)$"),
        )
        self._definitions[SyntaxRegistryKey.NUMBERED_LIST] = definition

    def _register_quote_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="> ",
            end_delimiter="",
            regex_pattern=re.compile(r"^>(?!>)\s*(.+)$"),
        )
        self._definitions[SyntaxRegistryKey.QUOTE] = definition

    def _register_table_syntax(self) -> None:
        delimiter = self._markdown_grammar.table_delimiter
        definition = SyntaxDefinition(
            start_delimiter=delimiter,
            end_delimiter="",
            regex_pattern=re.compile(rf"^\s*{re.escape(delimiter)}(.+){re.escape(delimiter)}\s*$"),
        )
        self._definitions[SyntaxRegistryKey.TABLE] = definition

    def _register_table_row_syntax(self) -> None:
        delimiter = self._markdown_grammar.table_delimiter
        definition = SyntaxDefinition(
            start_delimiter=delimiter,
            end_delimiter="",
            regex_pattern=re.compile(rf"^\s*{re.escape(delimiter)}([\s\-:|]+){re.escape(delimiter)}\s*$"),
        )
        self._definitions[SyntaxRegistryKey.TABLE_ROW] = definition

    def _register_table_of_contents_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[toc]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[toc\]$", re.IGNORECASE),
        )
        self._definitions[SyntaxRegistryKey.TABLE_OF_CONTENTS] = definition

    def _register_todo_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="- [ ]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\s*-\s+\[ \]\s+(.+)$"),
        )
        self._definitions[SyntaxRegistryKey.TO_DO] = definition

    def _register_todo_done_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="- [x]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\s*-\s+\[x\]\s+(.+)$", re.IGNORECASE),
        )
        self._definitions[SyntaxRegistryKey.TO_DO_DONE] = definition

    def _register_toggle_syntax(self) -> None:
        delimiter = self._markdown_grammar.toggle_delimiter
        definition = SyntaxDefinition(
            start_delimiter=delimiter,
            end_delimiter=delimiter,
            regex_pattern=re.compile(rf"^{re.escape(delimiter)}\s+(.+)$"),
            end_regex_pattern=re.compile(rf"^{re.escape(delimiter)}\s*$"),
        )
        self._definitions[SyntaxRegistryKey.TOGGLE] = definition

    def _register_toggleable_heading_syntax(self) -> None:
        delimiter = self._markdown_grammar.toggle_delimiter
        escaped_delimiter = re.escape(delimiter)
        definition = SyntaxDefinition(
            start_delimiter=f"{delimiter} #",
            end_delimiter=delimiter,
            regex_pattern=re.compile(rf"^{escaped_delimiter}\s*(?P<level>#{{1,3}})(?!#)\s*(.+)$", re.IGNORECASE),
            end_regex_pattern=re.compile(rf"^{escaped_delimiter}\s*$"),
        )
        self._definitions[SyntaxRegistryKey.TOGGLEABLE_HEADING] = definition

    def _register_caption_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[caption]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[caption\]\s+(\S.*)$"),
        )
        self._definitions[SyntaxRegistryKey.CAPTION] = definition

    def _register_space_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="[space]",
            end_delimiter="",
            regex_pattern=re.compile(r"^\[space\]\s*$"),
        )
        self._definitions[SyntaxRegistryKey.SPACE] = definition

    def _register_heading_syntax(self) -> None:
        definition = SyntaxDefinition(
            start_delimiter="#",
            end_delimiter="",
            regex_pattern=re.compile(r"^(#{1,3})[ \t]+(.+)$"),
        )
        self._definitions[SyntaxRegistryKey.HEADING] = definition
