from notionary.page.content.syntax.definition.models import SyntaxDefinitionRegistryKey
from notionary.page.content.syntax.definition.registry import SyntaxDefinitionRegistry
from notionary.page.content.syntax.prompts.models import SyntaxPromptData


# Add a builder for comprehensive analysis (or entrys for getters here (test with llm) - acces thsi here from top level
# also acces single element syntax
class SyntaxPromptRegistry:
    def __init__(self, syntax_definition_registry: SyntaxDefinitionRegistry):
        self._syntax_definition_registry = syntax_definition_registry
        self._prompts: dict[SyntaxDefinitionRegistryKey, SyntaxPromptData] = {}
        self._register_defaults()

    def get_prompt_data(self, key: SyntaxDefinitionRegistryKey) -> SyntaxPromptData:
        return self._prompts[key]

    def get_all_prompt_data(self) -> dict[SyntaxDefinitionRegistryKey, SyntaxPromptData]:
        return self._prompts.copy()

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
        self._register_toggleable_heading_prompt()
        self._register_callout_prompt()
        self._register_code_prompt()
        self._register_column_list_prompt()
        self._register_column_prompt()
        self._register_equation_prompt()

        # Text blocks
        self._register_quote_prompt()
        self._register_heading_prompt()
        self._register_divider_prompt()
        self._register_breadcrumb_prompt()
        self._register_table_of_contents_prompt()
        self._register_table_prompt()
        self._register_table_row_prompt()
        self._register_caption_prompt()
        self._register_space_prompt()

    # Media elements
    def _register_audio_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.AUDIO] = SyntaxPromptData(
            description="Embeds an audio file into the page. Supports various audio formats like MP3, WAV, OGG.",
            is_multi_line=False,
            few_shot_examples=[
                "[audio](https://example.com/song.mp3)",
                "[audio](path/to/audio/file.wav)",
                "[audio](https://cdn.example.com/podcast-episode-1.ogg)",
            ],
        )

    def _register_video_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.VIDEO] = SyntaxPromptData(
            description="Embeds a video file into the page. Supports various video formats like MP4, WebM, AVI.",
            is_multi_line=False,
            few_shot_examples=[
                "[video](https://example.com/movie.mp4)",
                "[video](path/to/video/file.webm)",
                "[video](https://cdn.example.com/tutorial.mp4)",
            ],
        )

    def _register_image_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.IMAGE] = SyntaxPromptData(
            description="Embeds an image into the page. Supports formats like PNG, JPG, GIF, WebP.",
            is_multi_line=False,
            few_shot_examples=[
                "[image](https://example.com/photo.jpg)",
                "[image](path/to/image.png)",
                "[image](https://cdn.example.com/diagram.svg)",
            ],
        )

    def _register_file_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.FILE] = SyntaxPromptData(
            description="Links to a downloadable file. Can be used for any file type.",
            is_multi_line=False,
            few_shot_examples=[
                "[file](https://example.com/document.docx)",
                "[file](path/to/archive.zip)",
                "[file](https://cdn.example.com/spreadsheet.xlsx)",
            ],
        )

    def _register_pdf_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.PDF] = SyntaxPromptData(
            description="Embeds a PDF document into the page for inline viewing.",
            is_multi_line=False,
            few_shot_examples=[
                "[pdf](https://example.com/document.pdf)",
                "[pdf](path/to/report.pdf)",
                "[pdf](https://cdn.example.com/whitepaper.pdf)",
            ],
        )

    def _register_bookmark_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.BOOKMARK] = SyntaxPromptData(
            description="Creates a bookmark link to an external URL. Only accepts HTTP/HTTPS URLs.",
            is_multi_line=False,
            few_shot_examples=[
                "[bookmark](https://example.com)",
                "[bookmark](https://github.com/project)",
                "[bookmark](https://docs.example.com/guide)",
            ],
        )

    def _register_embed_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.EMBED] = SyntaxPromptData(
            description="Embeds external content (like YouTube videos, tweets, etc.) into the page.",
            is_multi_line=False,
            few_shot_examples=[
                "[embed](https://www.youtube.com/watch?v=dQw4w9WgXcQ)",
                "[embed](https://twitter.com/user/status/123456789)",
                "[embed](https://open.spotify.com/track/xyz)",
            ],
        )

    # Lists
    def _register_bulleted_list_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.BULLETED_LIST] = SyntaxPromptData(
            description="Creates a bulleted (unordered) list item. Can be nested with indentation.",
            is_multi_line=False,
            few_shot_examples=[
                "- First item",
                "- Second item",
                "  - Nested item (indented with 2 spaces)",
            ],
        )

    def _register_numbered_list_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.NUMBERED_LIST] = SyntaxPromptData(
            description="Creates a numbered (ordered) list item. Can be nested with indentation.",
            is_multi_line=False,
            few_shot_examples=[
                "1. First step",
                "2. Second step",
                "  1. Sub-step (indented with 2 spaces)",
            ],
        )

    def _register_todo_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TO_DO] = SyntaxPromptData(
            description="Creates an unchecked todo item.",
            is_multi_line=False,
            few_shot_examples=[
                "- [ ] Task to complete",
                "- [ ] Buy groceries",
                "- [ ] Write documentation",
            ],
        )

    def _register_todo_done_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TO_DO_DONE] = SyntaxPromptData(
            description="Creates a checked (completed) todo item.",
            is_multi_line=False,
            few_shot_examples=[
                "- [x] Completed task",
                "- [x] Fixed the bug",
                "- [x] Deployed to production",
            ],
        )

    # Block containers
    def _register_toggle_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TOGGLE] = SyntaxPromptData(
            description="Creates a toggleable/collapsible section with a title. Content between delimiters can be shown/hidden.",
            is_multi_line=True,
            few_shot_examples=[
                "+++  Click to expand\nHidden content here\n+++",
                "+++  FAQ Answer\nDetailed explanation...\n+++",
                "+++  Show more details\nAdditional information\n+++",
            ],
        )

    def _register_toggleable_heading_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TOGGLEABLE_HEADING] = SyntaxPromptData(
            description="Creates a heading that can be toggled to show/hide content beneath it.",
            is_multi_line=True,
            few_shot_examples=[
                "+++  # Main Section\nSection content\n+++",
                "+++  ## Subsection\nSubsection content\n+++",
                "+++  ### Details\nDetailed information\n+++",
            ],
        )

    def _register_callout_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.CALLOUT] = SyntaxPromptData(
            description="Creates a highlighted callout box with optional emoji/icon and title.",
            is_multi_line=False,
            few_shot_examples=[
                '[callout](💡 "Pro Tip")',
                '[callout](⚠️ "Warning")',
                '[callout](📌 "Important Note")',
            ],
        )

    def _register_code_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.CODE] = SyntaxPromptData(
            description="Creates a code block with optional syntax highlighting. Specify language after opening delimiter.",
            is_multi_line=True,
            few_shot_examples=[
                "```python\nprint('Hello, World!')\n```",
                "```javascript\nconsole.log('Hello!');\n```",
                "```\nPlain text code\n```",
            ],
        )

    def _register_column_list_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.COLUMN_LIST] = SyntaxPromptData(
            description="Creates a container for multiple columns. Use with column blocks inside.",
            is_multi_line=True,
            few_shot_examples=[
                "+++  columns\n[column content]\n+++",
                "+++  columns\n+++  column\nFirst column\n+++\n+++  column\nSecond column\n+++\n+++",
            ],
        )

    def _register_column_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.COLUMN] = SyntaxPromptData(
            description="Creates a single column within a column list. Optional width ratio (0.0-1.0).",
            is_multi_line=True,
            few_shot_examples=[
                "+++  column\nColumn content\n+++",
                "+++  column 0.5\nHalf width column\n+++",
                "+++  column 0.33\nOne third width\n+++",
            ],
        )

    def _register_equation_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.EQUATION] = SyntaxPromptData(
            description="Creates a mathematical equation block using LaTeX syntax.",
            is_multi_line=True,
            few_shot_examples=[
                "$$\nE = mc^2\n$$",
                "$$\n\\frac{-b \\pm \\sqrt{b^2-4ac}}{2a}\n$$",
                "$$\n\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}\n$$",
            ],
        )

    # Text blocks
    def _register_quote_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.QUOTE] = SyntaxPromptData(
            description="Creates a block quote for citing text or highlighting quotations.",
            is_multi_line=False,
            few_shot_examples=[
                "> This is a quote",
                "> To be or not to be",
                "> Multi-word quoted text",
            ],
        )

    def _register_heading_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.HEADING] = SyntaxPromptData(
            description="Creates a heading. Use 1-3 # symbols for different heading levels.",
            is_multi_line=False,
            few_shot_examples=[
                "# Heading 1 (largest)",
                "## Heading 2 (medium)",
                "### Heading 3 (smallest)",
            ],
        )

    def _register_divider_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.DIVIDER] = SyntaxPromptData(
            description="Creates a horizontal divider line to separate content sections.",
            is_multi_line=False,
            few_shot_examples=[
                "---",
                "----",
                "-----",
            ],
        )

    def _register_breadcrumb_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.BREADCRUMB] = SyntaxPromptData(
            description="Creates a breadcrumb navigation element showing the current page hierarchy.",
            is_multi_line=False,
            few_shot_examples=[
                "[breadcrumb]",
            ],
        )

    def _register_table_of_contents_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TABLE_OF_CONTENTS] = SyntaxPromptData(
            description="Generates a table of contents based on the headings in the document.",
            is_multi_line=False,
            few_shot_examples=[
                "[toc]",
                "[TOC]",
            ],
        )

    def _register_table_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TABLE] = SyntaxPromptData(
            description="Creates a table row with cells separated by the table delimiter.",
            is_multi_line=False,
            few_shot_examples=[
                "|Header 1|Header 2|Header 3|",
                "|Cell 1|Cell 2|Cell 3|",
                "|Data A|Data B|Data C|",
            ],
        )

    def _register_table_row_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.TABLE_ROW] = SyntaxPromptData(
            description="Creates a table header separator row with alignment markers.",
            is_multi_line=False,
            few_shot_examples=[
                "|---|---|---|",
                "|:---|:---:|---:|",
                "|-|-|-|",
            ],
        )

    def _register_caption_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.CAPTION] = SyntaxPromptData(
            description="Adds a caption to the preceding element (like an image or table).",
            is_multi_line=False,
            few_shot_examples=[
                "[caption] Figure 1: Architecture diagram",
                "[caption] Table showing quarterly results",
                "[caption] Screenshot of the interface",
            ],
        )

    def _register_space_prompt(self) -> None:
        self._prompts[SyntaxDefinitionRegistryKey.SPACE] = SyntaxPromptData(
            description="Inserts a blank space/line for visual separation.",
            is_multi_line=False,
            few_shot_examples=[
                "[space]",
            ],
        )
