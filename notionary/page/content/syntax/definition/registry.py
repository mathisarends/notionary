import re

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.page.content.syntax.definition.models import (
    EnclosedSyntaxDefinition,
    SimpleSyntaxDefinition,
    SyntaxDefinition,
    SyntaxDefinitionRegistryKey,
)
from notionary.utils.decorators import singleton


@singleton
class SyntaxDefinitionRegistry:
    def __init__(
        self, markdown_markdown_grammar: MarkdownGrammar | None = None
    ) -> None:
        self._markdown_grammar = markdown_markdown_grammar or MarkdownGrammar()
        self._definitions: dict[SyntaxDefinitionRegistryKey, SyntaxDefinition] = {}
        self._register_defaults()

    def get_breadcrumb_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.BREADCRUMB]

    def get_bulleted_list_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.BULLETED_LIST]

    def get_divider_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.DIVIDER]

    def get_numbered_list_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.NUMBERED_LIST]

    def get_quote_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.QUOTE]

    def get_table_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.TABLE]

    def get_table_row_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.TABLE_ROW]

    def get_table_of_contents_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS]

    def get_todo_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.TO_DO]

    def get_todo_done_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.TO_DO_DONE]

    def get_caption_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.CAPTION]

    def get_space_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.SPACE]

    def get_heading_syntax(self) -> SimpleSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.HEADING]

    def get_audio_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.AUDIO]

    def get_bookmark_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.BOOKMARK]

    def get_embed_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.EMBED]

    def get_file_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.FILE]

    def get_image_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.IMAGE]

    def get_pdf_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.PDF]

    def get_video_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.VIDEO]

    def get_callout_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.CALLOUT]

    def get_code_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.CODE]

    def get_column_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.COLUMN]

    def get_column_list_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.COLUMN_LIST]

    def get_equation_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.EQUATION]

    def get_toggle_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.TOGGLE]

    def get_toggleable_heading_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.TOGGLEABLE_HEADING]

    def get_synced_block_syntax(self) -> EnclosedSyntaxDefinition:
        return self._definitions[SyntaxDefinitionRegistryKey.SYNCED_BLOCK]

    def _create_media_syntax(
        self, media_type: str, url_pattern: str | None = None
    ) -> EnclosedSyntaxDefinition:
        return EnclosedSyntaxDefinition(
            start_delimiter=f"[{media_type}](",
            end_delimiter=")",
            regex_pattern=self._markdown_grammar.media_block_pattern(
                media_type, url_pattern
            ),
            end_regex_pattern=self._markdown_grammar.media_end_pattern,
        )

    def _create_url_media_syntax(self, media_type: str) -> EnclosedSyntaxDefinition:
        return EnclosedSyntaxDefinition(
            start_delimiter=f"[{media_type}](",
            end_delimiter=")",
            regex_pattern=self._markdown_grammar.url_media_block_pattern(media_type),
            end_regex_pattern=self._markdown_grammar.media_end_pattern,
        )

    def _register_defaults(self) -> None:
        # Media elements (enclosed)
        self._register_audio_syntax()
        self._register_video_syntax()
        self._register_image_syntax()
        self._register_file_syntax()
        self._register_pdf_syntax()
        self._register_bookmark_syntax()
        self._register_embed_syntax()

        # Lists (simple)
        self._register_bulleted_list_syntax()
        self._register_numbered_list_syntax()
        self._register_todo_syntax()
        self._register_todo_done_syntax()

        # Block containers (enclosed)
        self._register_synced_block_syntax()
        self._register_toggle_syntax()
        self._register_toggleable_heading_syntax()
        self._register_callout_syntax()
        self._register_code_syntax()
        self._register_column_list_syntax()
        self._register_column_syntax()
        self._register_equation_syntax()

        # Text blocks (simple)
        self._register_quote_syntax()
        self._register_heading_syntax()
        self._register_divider_syntax()
        self._register_breadcrumb_syntax()
        self._register_table_of_contents_syntax()
        self._register_table_syntax()
        self._register_table_row_syntax()
        self._register_caption_syntax()
        self._register_space_syntax()

    # Registration methods - SimpleSyntaxDefinition
    def _register_breadcrumb_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.breadcrumb_delimiter,
            regex_pattern=self._markdown_grammar.breadcrumb_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.BREADCRUMB] = definition

    def _register_bulleted_list_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.bulleted_list_delimiter,
            regex_pattern=self._markdown_grammar.bulleted_list_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.BULLETED_LIST] = definition

    def _register_divider_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.divider_delimiter,
            regex_pattern=self._markdown_grammar.divider_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.DIVIDER] = definition

    def _register_numbered_list_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.numbered_list_delimiter,
            regex_pattern=self._markdown_grammar.numbered_list_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.NUMBERED_LIST] = definition

    def _register_quote_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.quote_delimiter,
            regex_pattern=self._markdown_grammar.quote_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.QUOTE] = definition

    def _register_table_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.table_delimiter,
            regex_pattern=self._markdown_grammar.table_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.TABLE] = definition

    def _register_table_row_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.table_delimiter,
            regex_pattern=self._markdown_grammar.table_row_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.TABLE_ROW] = definition

    def _register_table_of_contents_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.table_of_contents_delimiter,
            regex_pattern=self._markdown_grammar.table_of_contents_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS] = definition

    def _register_todo_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.todo_delimiter,
            regex_pattern=self._markdown_grammar.todo_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.TO_DO] = definition

    def _register_todo_done_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.todo_done_delimiter,
            regex_pattern=self._markdown_grammar.todo_done_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.TO_DO_DONE] = definition

    def _register_caption_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.caption_delimiter,
            regex_pattern=self._markdown_grammar.caption_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.CAPTION] = definition

    def _register_space_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.space_delimiter,
            regex_pattern=self._markdown_grammar.space_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.SPACE] = definition

    def _register_heading_syntax(self) -> None:
        definition = SimpleSyntaxDefinition(
            start_delimiter=self._markdown_grammar.heading_delimiter,
            regex_pattern=self._markdown_grammar.heading_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.HEADING] = definition

    # Registration methods - EnclosedSyntaxDefinition
    def _register_audio_syntax(self) -> None:
        self._definitions[SyntaxDefinitionRegistryKey.AUDIO] = (
            self._create_media_syntax("audio")
        )

    def _register_video_syntax(self) -> None:
        self._definitions[SyntaxDefinitionRegistryKey.VIDEO] = (
            self._create_media_syntax("video")
        )

    def _register_image_syntax(self) -> None:
        self._definitions[SyntaxDefinitionRegistryKey.IMAGE] = (
            self._create_media_syntax("image")
        )

    def _register_file_syntax(self) -> None:
        self._definitions[SyntaxDefinitionRegistryKey.FILE] = self._create_media_syntax(
            "file"
        )

    def _register_pdf_syntax(self) -> None:
        self._definitions[SyntaxDefinitionRegistryKey.PDF] = self._create_media_syntax(
            "pdf"
        )

    def _register_bookmark_syntax(self) -> None:
        self._definitions[SyntaxDefinitionRegistryKey.BOOKMARK] = (
            self._create_url_media_syntax("bookmark")
        )

    def _register_embed_syntax(self) -> None:
        self._definitions[SyntaxDefinitionRegistryKey.EMBED] = (
            self._create_url_media_syntax("embed")
        )

    def _register_callout_syntax(self) -> None:
        definition = EnclosedSyntaxDefinition(
            start_delimiter=self._markdown_grammar.callout_delimiter,
            end_delimiter=self._markdown_grammar.media_end_delimiter,
            regex_pattern=self._markdown_grammar.callout_pattern,
            end_regex_pattern=self._markdown_grammar.callout_end_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.CALLOUT] = definition

    def _register_code_syntax(self) -> None:
        definition = EnclosedSyntaxDefinition(
            start_delimiter=self._markdown_grammar.code_delimiter,
            end_delimiter=self._markdown_grammar.code_delimiter,
            regex_pattern=self._markdown_grammar.code_start_pattern,
            end_regex_pattern=self._markdown_grammar.code_end_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.CODE] = definition

    def _register_column_syntax(self) -> None:
        delimiter = self._markdown_grammar.column_delimiter
        definition = EnclosedSyntaxDefinition(
            start_delimiter=f"{delimiter} column",
            end_delimiter=delimiter,
            regex_pattern=self._markdown_grammar.column_pattern,
            end_regex_pattern=self._markdown_grammar.column_end_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.COLUMN] = definition

    def _register_column_list_syntax(self) -> None:
        delimiter = self._markdown_grammar.column_delimiter
        definition = EnclosedSyntaxDefinition(
            start_delimiter=f"{delimiter} columns",
            end_delimiter=delimiter,
            regex_pattern=self._markdown_grammar.column_list_pattern,
            end_regex_pattern=self._markdown_grammar.column_list_end_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.COLUMN_LIST] = definition

    def _register_equation_syntax(self) -> None:
        definition = EnclosedSyntaxDefinition(
            start_delimiter=self._markdown_grammar.equation_delimiter,
            end_delimiter=self._markdown_grammar.equation_delimiter,
            regex_pattern=self._markdown_grammar.equation_start_pattern,
            end_regex_pattern=self._markdown_grammar.equation_end_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.EQUATION] = definition

    def _register_toggle_syntax(self) -> None:
        definition = EnclosedSyntaxDefinition(
            start_delimiter=self._markdown_grammar.toggle_delimiter,
            end_delimiter=self._markdown_grammar.toggle_delimiter,
            regex_pattern=self._markdown_grammar.toggle_pattern,
            end_regex_pattern=self._markdown_grammar.toggle_end_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.TOGGLE] = definition

    def _register_toggleable_heading_syntax(self) -> None:
        delimiter = self._markdown_grammar.toggle_delimiter
        definition = EnclosedSyntaxDefinition(
            start_delimiter=f"{delimiter} #",
            end_delimiter=delimiter,
            regex_pattern=self._markdown_grammar.toggleable_heading_pattern,
            end_regex_pattern=self._markdown_grammar.toggleable_heading_end_pattern,
        )
        self._definitions[SyntaxDefinitionRegistryKey.TOGGLEABLE_HEADING] = definition

    def _register_synced_block_syntax(self) -> None:
        delimiter = ">>>"
        definition = EnclosedSyntaxDefinition(
            start_delimiter=delimiter,
            end_delimiter="",
            regex_pattern=re.compile(rf"^{re.escape(delimiter)}\s+(.+)$"),
            end_regex_pattern=re.compile(r"^$"),
        )
        self._definitions[SyntaxDefinitionRegistryKey.SYNCED_BLOCK] = definition
