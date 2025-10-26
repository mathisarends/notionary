import json
from dataclasses import asdict

from notionary.page.content.syntax.definition.grammar import MarkdownGrammar
from notionary.page.content.syntax.definition.models import SyntaxDefinitionRegistryKey
from notionary.page.content.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.syntax.prompts.models import SyntaxPromptData


class SyntaxPromptRegistry:
    def __init__(
        self,
        syntax_definition_registry: SyntaxDefinitionRegistry | None = None,
        markdown_grammar: MarkdownGrammar | None = None,
    ):
        self._syntax_definition_registry = (
            syntax_definition_registry or SyntaxDefinitionRegistry()
        )
        self._grammar = markdown_grammar or MarkdownGrammar()
        self._prompts: dict[SyntaxDefinitionRegistryKey, SyntaxPromptData] = {}
        self._register_defaults()

    def get_prompt_data(self, key: SyntaxDefinitionRegistryKey) -> SyntaxPromptData:
        return self._prompts[key]

    def get_all_prompt_data_as_json(self, indent: int | None = 2) -> str:
        prompts_dict = self._prompts.copy()

        json_compatible_dict = {
            key.value: asdict(value) for key, value in prompts_dict.items()
        }

        return json.dumps(json_compatible_dict, indent=indent, ensure_ascii=False)

    def get_breadcrumb_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.BREADCRUMB]

    def get_bulleted_list_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.BULLETED_LIST]

    def get_divider_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.DIVIDER]

    def get_numbered_list_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.NUMBERED_LIST]

    def get_quote_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.QUOTE]

    def get_table_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.TABLE]

    def get_table_of_contents_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS]

    def get_todo_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.TO_DO]

    def get_todo_done_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.TO_DO_DONE]

    def get_caption_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.CAPTION]

    def get_space_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.SPACE]

    def get_heading_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.HEADING]

    def get_audio_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.AUDIO]

    def get_bookmark_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.BOOKMARK]

    def get_embed_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.EMBED]

    def get_file_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.FILE]

    def get_image_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.IMAGE]

    def get_pdf_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.PDF]

    def get_video_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.VIDEO]

    def get_callout_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.CALLOUT]

    def get_code_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.CODE]

    def get_column_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.COLUMN_LIST]

    def get_equation_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.EQUATION]

    def get_toggle_prompt(self) -> SyntaxPromptData:
        return self._prompts[SyntaxDefinitionRegistryKey.TOGGLE]

    def _get_nesting_info(self) -> str:
        return f"Can be nested by indenting with {self._grammar.spaces_per_nesting_level} spaces per level."

    def _get_media_path_usage_notes(self) -> str:
        return (
            "Accepts both URLs (starting with http:// or https://) and local file paths. "
            "For local files, use relative or absolute paths WITHOUT http/https prefix. "
            "Examples: 'images/photo.jpg' or '/home/user/document.pdf'. "
            "Do NOT prefix local file paths with http:// or https://."
        )

    def _generate_url_media_examples(
        self, start_delimiter: str, end_delimiter: str, example_urls: list[str]
    ) -> list[str]:
        return [f"{start_delimiter}{url}{end_delimiter}" for url in example_urls]

    def _register_defaults(self) -> None:
        # Media elements
        self._register_audio_prompt()
        self._register_video_prompt()
        self._register_image_prompt()
        self._register_file_prompt()
        self._register_pdf_prompt()
        self._register_bookmark_prompt()
        self._register_embed_prompt()

        # Lists
        self._register_bulleted_list_prompt()
        self._register_numbered_list_prompt()
        self._register_todo_prompt()
        self._register_todo_done_prompt()

        # Block containers
        self._register_toggle_prompt()
        self._register_callout_prompt()
        self._register_code_prompt()
        self._register_column_prompt()
        self._register_equation_prompt()

        # Text blocks
        self._register_quote_prompt()
        self._register_heading_prompt()
        self._register_divider_prompt()
        self._register_breadcrumb_prompt()
        self._register_table_of_contents_prompt()
        self._register_table_prompt()
        self._register_caption_prompt()
        self._register_space_prompt()

    # Media elements
    def _register_audio_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_audio_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.AUDIO] = SyntaxPromptData(
            element="Audio",
            description="Embeds an audio file into the page. Supports various audio formats like MP3, WAV, OGG.",
            is_multi_line=False,
            few_shot_examples=self._generate_audio_examples(
                definition.start_delimiter, definition.end_delimiter
            ),
            usage_notes=self._get_media_path_usage_notes(),
            supports_inline_rich_text=False,
        )

    def _generate_audio_examples(
        self, start_delimiter: str, end_delimiter: str
    ) -> list[str]:
        """Generate valid audio examples with real audio file extensions."""
        return [
            f"{start_delimiter}https://example.com/audio.mp3{end_delimiter}",
            f"{start_delimiter}https://example.com/sound.wav{end_delimiter}",
            f"{start_delimiter}https://example.com/music.ogg{end_delimiter}",
        ]

    def _register_video_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_video_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.VIDEO] = SyntaxPromptData(
            element="Video",
            description="Embeds a video file into the page. Supports various video formats like MP4, WebM, AVI.",
            is_multi_line=False,
            few_shot_examples=self._generate_video_examples(
                definition.start_delimiter, definition.end_delimiter
            ),
            usage_notes=self._get_media_path_usage_notes(),
            supports_inline_rich_text=False,
        )

    def _generate_video_examples(
        self, start_delimiter: str, end_delimiter: str
    ) -> list[str]:
        """Generate valid video examples with real video file extensions."""
        return [
            f"{start_delimiter}https://example.com/video.mp4{end_delimiter}",
            f"{start_delimiter}https://example.com/clip.mov{end_delimiter}",
            f"{start_delimiter}https://www.youtube.com/watch?v=dQw4w9WgXcQ{end_delimiter}",
        ]

    def _register_image_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_image_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.IMAGE] = SyntaxPromptData(
            element="Image",
            description="Embeds an image into the page. Supports formats like PNG, JPG, GIF, WebP.",
            is_multi_line=False,
            few_shot_examples=self._generate_image_examples(
                definition.start_delimiter, definition.end_delimiter
            ),
            usage_notes=self._get_media_path_usage_notes(),
            supports_inline_rich_text=False,
        )

    def _generate_image_examples(
        self, start_delimiter: str, end_delimiter: str
    ) -> list[str]:
        """Generate valid image examples with real image file extensions."""
        return [
            f"{start_delimiter}https://example.com/photo.jpg{end_delimiter}",
            f"{start_delimiter}https://example.com/image.png{end_delimiter}",
            f"{start_delimiter}https://example.com/graphic.webp{end_delimiter}",
        ]

    def _register_file_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_file_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.FILE] = SyntaxPromptData(
            element="File",
            description="Links to a downloadable file. Can be used for any file type.",
            is_multi_line=False,
            few_shot_examples=self._generate_file_examples(
                definition.start_delimiter, definition.end_delimiter
            ),
            usage_notes=self._get_media_path_usage_notes(),
            supports_inline_rich_text=False,
        )

    def _generate_file_examples(
        self, start_delimiter: str, end_delimiter: str
    ) -> list[str]:
        """Generate valid file examples with various file extensions."""
        return [
            f"{start_delimiter}https://example.com/document.docx{end_delimiter}",
            f"{start_delimiter}https://example.com/archive.zip{end_delimiter}",
            f"{start_delimiter}https://example.com/data.csv{end_delimiter}",
        ]

    def _register_pdf_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_pdf_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.PDF] = SyntaxPromptData(
            element="PDF",
            description="Embeds a PDF document into the page for inline viewing.",
            is_multi_line=False,
            few_shot_examples=self._generate_pdf_examples(
                definition.start_delimiter, definition.end_delimiter
            ),
            usage_notes=self._get_media_path_usage_notes(),
            supports_inline_rich_text=False,
        )

    def _generate_pdf_examples(
        self, start_delimiter: str, end_delimiter: str
    ) -> list[str]:
        """Generate valid PDF examples."""
        return [
            f"{start_delimiter}https://example.com/document.pdf{end_delimiter}",
            f"{start_delimiter}https://example.com/manual.pdf{end_delimiter}",
            f"{start_delimiter}https://example.com/report.pdf{end_delimiter}",
        ]

    def _register_bookmark_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_bookmark_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.BOOKMARK] = SyntaxPromptData(
            element="Bookmark",
            description="Creates a bookmark link to an external URL. Only accepts HTTP/HTTPS URLs.",
            is_multi_line=False,
            few_shot_examples=self._generate_url_media_examples(
                definition.start_delimiter,
                definition.end_delimiter,
                [
                    "https://example.com",
                    "https://github.com/project",
                    "https://docs.example.com/guide",
                ],
            ),
            usage_notes=(
                "Only accepts HTTP/HTTPS URLs. "
                "Use the full URL including the protocol. "
                "Cannot reference local files."
            ),
            supports_inline_rich_text=False,
        )

    def _register_embed_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_embed_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.EMBED] = SyntaxPromptData(
            element="Embed",
            description="Embeds external content (like YouTube videos, tweets, etc.) into the page.",
            is_multi_line=False,
            few_shot_examples=self._generate_url_media_examples(
                definition.start_delimiter,
                definition.end_delimiter,
                [
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "https://twitter.com/user/status/123456789",
                    "https://open.spotify.com/track/xyz",
                ],
            ),
            usage_notes=(
                "Only accepts HTTP/HTTPS URLs from supported platforms. "
                "Use the full shareable URL from the platform."
            ),
            supports_inline_rich_text=False,
        )

    # Lists
    def _register_bulleted_list_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_bulleted_list_syntax()
        spaces = " " * self._grammar.spaces_per_nesting_level
        self._prompts[SyntaxDefinitionRegistryKey.BULLETED_LIST] = SyntaxPromptData(
            element="Bulleted List",
            description=f"Creates a bulleted (unordered) list item. {self._get_nesting_info()}",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter}First item",
                f"{definition.start_delimiter}Second item",
                f"{spaces}{definition.start_delimiter}Nested item (indented with {self._grammar.spaces_per_nesting_level} spaces)",
            ],
            usage_notes=(
                f"Each list item is on its own line. "
                f"Nest items by indenting with exactly {self._grammar.spaces_per_nesting_level} spaces per level. "
                f"The content supports inline formatting like **bold**, *italic*, `code`, and links."
            ),
            supports_inline_rich_text=True,
        )

    def _register_numbered_list_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_numbered_list_syntax()
        spaces = " " * self._grammar.spaces_per_nesting_level
        self._prompts[SyntaxDefinitionRegistryKey.NUMBERED_LIST] = SyntaxPromptData(
            element="Numbered List",
            description=f"Creates a numbered (ordered) list item. {self._get_nesting_info()}",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter}First step",
                "2. Second step",
                f"{spaces}1. Sub-step (indented with {self._grammar.spaces_per_nesting_level} spaces)",
            ],
            usage_notes=(
                f"Each list item is on its own line. "
                f"The number is automatically incremented. "
                f"Nest items by indenting with exactly {self._grammar.spaces_per_nesting_level} spaces per level. "
                f"The content supports inline formatting like **bold**, *italic*, `code`, and links."
            ),
            supports_inline_rich_text=True,
        )

    def _register_todo_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_todo_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.TO_DO] = SyntaxPromptData(
            element="Todo",
            description=f"Creates an unchecked todo item. {self._get_nesting_info()}",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter} Task to complete",
                f"{definition.start_delimiter} Buy groceries",
                f"{definition.start_delimiter} Write documentation",
            ],
            usage_notes=(
                f"Each todo item is on its own line. Can be nested by indenting with {self._grammar.spaces_per_nesting_level} spaces. The content supports inline formatting."
            ),
            supports_inline_rich_text=True,
        )

    def _register_todo_done_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_todo_done_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.TO_DO_DONE] = SyntaxPromptData(
            element="Todo Done",
            description=f"Creates a checked (completed) todo item. {self._get_nesting_info()}",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter} Completed task",
                f"{definition.start_delimiter} Fixed the bug",
                f"{definition.start_delimiter} Deployed to production",
            ],
            usage_notes=(
                f"Each completed todo item is on its own line. "
                f"Can be nested by indenting with {self._grammar.spaces_per_nesting_level} spaces. "
                f"The content supports inline formatting."
            ),
            supports_inline_rich_text=True,
        )

    # Block containers
    def _register_toggle_prompt(self) -> None:
        delimiter = self._grammar.toggle_delimiter
        spaces = " " * self._grammar.spaces_per_nesting_level
        self._prompts[SyntaxDefinitionRegistryKey.TOGGLE] = SyntaxPromptData(
            element="Toggle",
            description="Creates a toggleable/collapsible section with a title. Content between delimiters can be shown/hidden.",
            is_multi_line=True,
            few_shot_examples=[
                (
                    f"{delimiter} Click to expand\n"
                    f"{spaces}Hidden content here\n"
                    f"{spaces}More hidden content"
                ),
                (
                    f"{delimiter} FAQ Answer\n"
                    f"{spaces}Detailed explanation...\n"
                    f"{spaces}Additional details"
                ),
                (
                    f"{delimiter} Show more details\n"
                    f"{spaces}Additional information\n"
                    f"{spaces}Even more content"
                ),
            ],
            usage_notes=(
                f"The toggle title (first line after {delimiter}) starts the collapsible section. "
                f"Content on subsequent lines indented by {self._grammar.spaces_per_nesting_level} spaces becomes children of the toggle. "
                f"The toggle ends when indentation returns to the original level. "
                f"The title supports inline formatting."
            ),
            supports_inline_rich_text=True,
        )

    def _register_callout_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_callout_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.CALLOUT] = SyntaxPromptData(
            element="Callout",
            description=f"Creates a highlighted callout box with optional emoji/icon and title. Children must be indented by {self._grammar.spaces_per_nesting_level} spaces.",
            is_multi_line=False,
            few_shot_examples=[
                f'{definition.start_delimiter}(💡 "Pro Tip")',
                f'{definition.start_delimiter}(⚠️ "Warning")',
                f'{definition.start_delimiter}(📌 "Important Note")',
            ],
            usage_notes=(
                f"The callout declaration is single-line, but can contain nested content on "
                f"subsequent lines indented by {self._grammar.spaces_per_nesting_level} spaces. "
                f"Format: emoji/icon followed by optional title in quotes. "
                f"The title supports inline formatting."
            ),
            supports_inline_rich_text=True,
        )

    def _register_code_prompt(self) -> None:
        delimiter = "```"
        self._prompts[SyntaxDefinitionRegistryKey.CODE] = SyntaxPromptData(
            element="Code",
            description="Creates a code block with optional syntax highlighting. Specify language after opening delimiter.",
            is_multi_line=True,
            few_shot_examples=[
                f"{delimiter}python\nprint('Hello, World!')\n{delimiter}",
                f"{delimiter}javascript\nconsole.log('Hello!');\n{delimiter}",
                f"{delimiter}\nPlain text code\n{delimiter}",
            ],
            usage_notes=(
                "Language identifier is optional but recommended for syntax highlighting. "
                "Content between delimiters is preserved exactly as written, including whitespace. "
                "NO inline formatting is supported inside code blocks."
            ),
            supports_inline_rich_text=False,
        )

    def _register_column_prompt(self) -> None:
        delimiter = self._grammar.column_delimiter
        spaces = " " * self._grammar.spaces_per_nesting_level
        self._prompts[SyntaxDefinitionRegistryKey.COLUMN_LIST] = SyntaxPromptData(
            element="Columns",
            description="Creates a multi-column layout. Requires at least 2 columns. Columns are defined by indentation.",
            is_multi_line=True,
            few_shot_examples=[
                (
                    f"{delimiter} columns\n"
                    f"{spaces}{delimiter} column\n"
                    f"{spaces * 2}First column content\n"
                    f"{spaces}{delimiter} column\n"
                    f"{spaces * 2}Second column content\n"
                ),
                (
                    f"{delimiter} columns\n"
                    f"{spaces}{delimiter} column 0.6\n"
                    f"{spaces * 2}Wide column (60%)\n"
                    f"{spaces * 2}More content here\n"
                    f"{spaces}{delimiter} column 0.4\n"
                    f"{spaces * 2}Narrow column (40%)\n"
                    f"{spaces * 2}Content here\n"
                ),
                (
                    f"{delimiter} columns\n"
                    f"{spaces}{delimiter} column\n"
                    f"{spaces * 2}Left column\n"
                    f"{spaces}{delimiter} column\n"
                    f"{spaces * 2}Middle column\n"
                    f"{spaces}{delimiter} column\n"
                    f"{spaces * 2}Right column\n"
                ),
            ],
            usage_notes=(
                f"Start with '{delimiter} columns' line. "
                f"Each column is defined with '{delimiter} column' indented by {self._grammar.spaces_per_nesting_level} spaces. "
                f"Column content must be indented by an additional {self._grammar.spaces_per_nesting_level} spaces (total {self._grammar.spaces_per_nesting_level * 2} spaces from start). "
                f"Optional width ratio (0.0-1.0) can be specified after 'column'. "
                f"At least 2 columns are required. "
                f"The column list ends when indentation returns to the original level. "
                f"Column content supports all other block elements and inline formatting."
            ),
            supports_inline_rich_text=True,
        )

    def _register_equation_prompt(self) -> None:
        delimiter = "$$"
        self._prompts[SyntaxDefinitionRegistryKey.EQUATION] = SyntaxPromptData(
            element="Equation",
            description="Creates a mathematical equation block using LaTeX syntax.",
            is_multi_line=True,
            few_shot_examples=[
                f"{delimiter}\nE = mc^2\n{delimiter}",
                f"{delimiter}\n\\frac{{-b \\pm \\sqrt{{b^2-4ac}}}}{{2a}}\n{delimiter}",
                f"{delimiter}\n\\sum_{{i=1}}^{{n}} i = \\frac{{n(n+1)}}{{2}}\n{delimiter}",
            ],
            usage_notes=(
                "Uses LaTeX syntax for mathematical notation. "
                "Content between delimiters is rendered as LaTeX. "
                "NO markdown formatting is supported, only LaTeX commands."
            ),
            supports_inline_rich_text=False,
        )

    # Text blocks
    def _register_quote_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_quote_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.QUOTE] = SyntaxPromptData(
            element="Quote",
            description=f"Creates a block quote for citing text or highlighting quotations. {self._get_nesting_info()}",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter}Single line quote",
                f"{definition.start_delimiter}First line\n{definition.start_delimiter}Second line\n{definition.start_delimiter}Third line",
                f"{definition.start_delimiter}Multi-paragraph quotes need multiple quote markers",
            ],
            usage_notes=(
                f"While marked as single-line syntax, quotes can span multiple lines by "
                f"prefixing each line with '{definition.start_delimiter}'. "
                f"Each line needs its own '{definition.start_delimiter}' prefix but they will "
                f"render as a continuous quote block. "
                f"The content supports inline formatting like **bold** and *italic*."
            ),
            supports_inline_rich_text=True,
        )

    def _register_heading_prompt(self) -> None:
        spaces = " " * self._grammar.spaces_per_nesting_level
        self._prompts[SyntaxDefinitionRegistryKey.HEADING] = SyntaxPromptData(
            element="Heading",
            description="Creates a heading. Use 1-3 # symbols for different heading levels. Becomes toggleable when followed by indented content.",
            is_multi_line=False,
            few_shot_examples=[
                "# Heading 1 (largest)",
                "## Heading 2 (medium)",
                "### Heading 3 (smallest)",
                (
                    f"## Toggleable Heading\n"
                    f"{spaces}This content is indented by {self._grammar.spaces_per_nesting_level} spaces\n"
                    f"{spaces}So it becomes a child of the heading\n"
                    f"{spaces}Making the heading toggleable\n"
                    f"\n"
                    f"Next paragraph ends the block"
                ),
            ],
            usage_notes=(
                f"Use # for top-level headings, ## for subsections, and ### for sub-subsections. "
                f"The heading text supports inline formatting like **bold**, *italic*, and `code`. "
                f"To make a heading toggleable, indent the following content by {self._grammar.spaces_per_nesting_level} spaces. "
                f"All indented content becomes collapsible children of the heading. "
                f"An empty line or content without indentation ends the toggleable block."
            ),
            supports_inline_rich_text=True,
        )

    def _register_divider_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_divider_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.DIVIDER] = SyntaxPromptData(
            element="Divider",
            description="Creates a horizontal divider line to separate content sections.",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter}",
                "----",
                "-----",
            ],
            usage_notes=(
                "Use at least three dashes. "
                "The divider is purely visual and contains no text content."
            ),
            supports_inline_rich_text=False,
        )

    def _register_breadcrumb_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_breadcrumb_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.BREADCRUMB] = SyntaxPromptData(
            element="Breadcrumb",
            description="Creates a breadcrumb navigation element showing the current page hierarchy.",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter}",
            ],
            usage_notes=(
                "Automatically generates breadcrumb navigation based on page hierarchy. "
                "No additional parameters or content needed."
            ),
            supports_inline_rich_text=False,
        )

    def _register_table_of_contents_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS] = SyntaxPromptData(
            element="Table of Contents",
            description="Generates a table of contents based on the headings in the document.",
            is_multi_line=False,
            few_shot_examples=[
                "[toc]",
                "[TOC]",
            ],
            usage_notes=(
                "Automatically generates a table of contents from all headings in the document. "
                "Case-insensitive. No additional parameters needed."
            ),
            supports_inline_rich_text=False,
        )

    def _register_table_prompt(self) -> None:
        delimiter = self._grammar.table_delimiter
        self._prompts[SyntaxDefinitionRegistryKey.TABLE] = SyntaxPromptData(
            element="Table",
            description=(
                "Creates a table with headers, separator row, and data rows. Cells are separated by delimiters."
            ),
            is_multi_line=False,
            few_shot_examples=[
                (
                    f"{delimiter}Header 1{delimiter}Header 2{delimiter}Header 3{delimiter}\n"
                    f"{delimiter}---{delimiter}---{delimiter}---{delimiter}\n"
                    f"{delimiter}Data 1{delimiter}Data 2{delimiter}Data 3{delimiter}\n"
                    f"{delimiter}More 1{delimiter}More 2{delimiter}More 3{delimiter}"
                ),
                (
                    f"{delimiter}Name{delimiter}Age{delimiter}City{delimiter}\n"
                    f"{delimiter}:---{delimiter}:---:{delimiter}---:{delimiter}\n"
                    f"{delimiter}Alice{delimiter}30{delimiter}NYC{delimiter}\n"
                    f"{delimiter}Bob{delimiter}25{delimiter}LA{delimiter}"
                ),
                (
                    f"{delimiter}Product{delimiter}Price{delimiter}Stock{delimiter}\n"
                    f"{delimiter}-{delimiter}-{delimiter}-{delimiter}\n"
                    f"{delimiter}Widget{delimiter}$10{delimiter}50{delimiter}\n"
                    f"{delimiter}Gadget{delimiter}$25{delimiter}30{delimiter}"
                ),
            ],
            usage_notes=(
                f"A table consists of: "
                f"(1) Header row with column names, "
                f"(2) Separator row with dashes "
                f"(use ':---' for left-align, ':---:' for center-align, '---:' for right-align), "
                f"(3) One or more data rows. "
                f"Each row is on its own line. "
                f"Cells are separated by '{delimiter}'. "
                f"The cell content supports inline formatting like **bold** and *italic*."
            ),
            supports_inline_rich_text=True,
        )

    def _register_caption_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_caption_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.CAPTION] = SyntaxPromptData(
            element="Caption",
            description="Adds a caption to the preceding element (like an image or table).",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter} Figure 1: Architecture diagram",
                f"{definition.start_delimiter} Table showing quarterly results",
                f"{definition.start_delimiter} Screenshot of the interface",
            ],
            usage_notes=(
                "Place immediately after the element you want to caption (image, table, etc.). "
                "The caption text supports inline formatting."
            ),
            supports_inline_rich_text=True,
        )

    def _register_space_prompt(self) -> None:
        definition = self._syntax_definition_registry.get_space_syntax()
        self._prompts[SyntaxDefinitionRegistryKey.SPACE] = SyntaxPromptData(
            element="Space",
            description="Inserts a blank space/line for visual separation.",
            is_multi_line=False,
            few_shot_examples=[
                f"{definition.start_delimiter}",
            ],
            usage_notes=(
                "Creates vertical whitespace between elements. "
                "No content or parameters needed."
            ),
            supports_inline_rich_text=False,
        )
