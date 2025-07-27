from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Union, Any, Dict
from pydantic import BaseModel


# ============================================================================
# ENUMS AND COMMON TYPES
# ============================================================================

BlockColor = Literal[
    "blue",
    "blue_background",
    "brown",
    "brown_background",
    "default",
    "gray",
    "gray_background",
    "green",
    "green_background",
    "orange",
    "orange_background",
    "yellow",
    "yellow_background",
    "pink",
    "pink_background",
    "purple",
    "purple_background",
    "red",
    "red_background",
]

BlockType = Literal[
    "bookmark",
    "breadcrumb",
    "bulleted_list_item",
    "callout",
    "child_database",
    "child_page",
    "column",
    "column_list",
    "code",
    "divider",
    "embed",
    "equation",
    "file",
    "heading_1",
    "heading_2",
    "heading_3",
    "image",
    "link_preview",
    "link_to_page",
    "numbered_list_item",
    "paragraph",
    "pdf",
    "quote",
    "synced_block",
    "table",
    "table_of_contents",
    "table_row",
    "template",
    "to_do",
    "toggle",
    "unsupported",
    "video",
    "audio",
]

CodeLanguage = Literal[
    "abap",
    "arduino",
    "bash",
    "basic",
    "c",
    "clojure",
    "coffeescript",
    "c++",
    "c#",
    "css",
    "dart",
    "diff",
    "docker",
    "elixir",
    "elm",
    "erlang",
    "flow",
    "fortran",
    "f#",
    "gherkin",
    "glsl",
    "go",
    "graphql",
    "groovy",
    "haskell",
    "html",
    "java",
    "javascript",
    "json",
    "julia",
    "kotlin",
    "latex",
    "less",
    "lisp",
    "livescript",
    "lua",
    "makefile",
    "markdown",
    "markup",
    "matlab",
    "mermaid",
    "nix",
    "objective-c",
    "ocaml",
    "pascal",
    "perl",
    "php",
    "plain text",
    "powershell",
    "prolog",
    "protobuf",
    "python",
    "r",
    "reason",
    "ruby",
    "rust",
    "sass",
    "scala",
    "scheme",
    "scss",
    "shell",
    "sql",
    "swift",
    "typescript",
    "vb.net",
    "verilog",
    "vhdl",
    "visual basic",
    "webassembly",
    "xml",
    "yaml",
    "java/c/c++/c#",
]


# ============================================================================
# RICH TEXT AND COMMON OBJECTS
# ============================================================================


class TextAnnotations(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: BlockColor = "default"


class TextContent(BaseModel):
    content: str
    link: Optional[Dict[str, str]] = None


class TextObject(BaseModel):
    type: Literal["text"]
    text: TextContent
    annotations: TextAnnotations = TextAnnotations()
    plain_text: str
    href: Optional[str] = None


class MentionDate(BaseModel):
    start: str
    end: Optional[str] = None
    time_zone: Optional[str] = None


class MentionUser(BaseModel):
    id: str
    object: Literal["user"] = "user"


class MentionPage(BaseModel):
    id: str


class MentionDatabase(BaseModel):
    id: str


class MentionObject(BaseModel):
    type: Literal[
        "user", "page", "database", "date", "link_preview", "template_mention"
    ]
    user: Optional[MentionUser] = None
    page: Optional[MentionPage] = None
    database: Optional[MentionDatabase] = None
    date: Optional[MentionDate] = None
    # Add other mention types as needed


@dataclass
class TextAnnotations:
    """Text formatting annotations"""

    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


@dataclass
class TextContent:
    """Text content with optional link"""

    content: str
    link: Optional[str] = None


class TextAnnotations(BaseModel):
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


class TextContent(BaseModel):
    content: str
    link: Optional[str] = None


class RichTextObject(BaseModel):
    type: str = "text"
    text: TextContent
    annotations: TextAnnotations
    plain_text: str
    href: Optional[str] = None

    @classmethod
    def from_plain_text(cls, content: str, **kwargs) -> RichTextObject:
        """Create rich text object from plain text with optional formatting."""
        annotations = TextAnnotations(**kwargs)
        text_content = TextContent(content=content, link=None)

        return cls(
            text=text_content, annotations=annotations, plain_text=content, href=None
        )


class PageMention(BaseModel):
    id: str


class MentionContent(BaseModel):
    type: Literal["page"] = "page"
    page: PageMention


class MentionRichText(BaseModel):
    type: Literal["mention"] = "mention"
    mention: MentionContent
    annotations: TextAnnotations
    plain_text: str
    href: Optional[str] = None

    @classmethod
    def from_page_id(cls, page_id: str) -> MentionRichText:
        page_mention = PageMention(id=page_id)
        mention_content = MentionContent(page=page_mention)
        return cls(
            mention=mention_content,
            annotations=TextAnnotations(),
            plain_text=f"@{page_id}",
            href=None,
        )


# ============================================================================
# FILE OBJECTS
# ============================================================================


class ExternalFile(BaseModel):
    url: str


class NotionHostedFile(BaseModel):
    url: str
    expiry_time: str


class FileUploadFile(BaseModel):
    id: str


class FileObject(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: Optional[list[RichTextObject]] = None
    name: Optional[str] = None


# ============================================================================
# EMOJI AND ICON OBJECTS
# ============================================================================


class EmojiIcon(BaseModel):
    type: Literal["emoji"] = "emoji"
    emoji: str


class FileIcon(BaseModel):
    type: Literal["file"] = "file"
    file: FileObject


IconObject = Union[EmojiIcon, FileIcon]


# ============================================================================
# PARENT OBJECTS
# ============================================================================


class PageParent(BaseModel):
    type: Literal["page_id"]
    page_id: str


class DatabaseParent(BaseModel):
    type: Literal["database_id"]
    database_id: str


class BlockParent(BaseModel):
    type: Literal["block_id"]
    block_id: str


class WorkspaceParent(BaseModel):
    type: Literal["workspace"]
    workspace: bool = True


ParentObject = Union[PageParent, DatabaseParent, BlockParent, WorkspaceParent]


# ============================================================================
# USER OBJECTS
# ============================================================================


class PartialUser(BaseModel):
    object: Literal["user"]
    id: str


# ============================================================================
# BLOCK TYPE OBJECTS
# ============================================================================


class AudioBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None


class BookmarkBlock(BaseModel):
    caption: list[RichTextObject] = []
    url: str


class BreadcrumbBlock(BaseModel):
    pass


class BulletedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: Optional[list["Block"]] = None


class CalloutBlock(BaseModel):
    rich_text: list[RichTextObject]
    icon: Optional[IconObject] = None
    color: BlockColor = "default"
    children: Optional[list["Block"]] = None


class ChildDatabaseBlock(BaseModel):
    title: str


class ChildPageBlock(BaseModel):
    title: str


class CodeBlock(BaseModel):
    caption: list[RichTextObject] = []
    rich_text: list[RichTextObject]
    language: CodeLanguage = "plain text"


class ColumnListBlock(BaseModel):
    pass


class ColumnBlock(BaseModel):
    width_ratio: Optional[float] = None


class DividerBlock(BaseModel):
    pass


class EmbedBlock(BaseModel):
    url: str


class EquationBlock(BaseModel):
    expression: str


class FileBlock(BaseModel):
    caption: list[RichTextObject] = []
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    name: Optional[str] = None


class HeadingBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    is_toggleable: bool = False
    children: Optional[list["Block"]] = None


class ImageBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: Optional[list[RichTextObject]] = None


class LinkPreviewBlock(BaseModel):
    url: str


class LinkToPageBlock(BaseModel):
    type: Literal["page_id", "database_id"]
    page_id: Optional[str] = None
    database_id: Optional[str] = None


class NumberedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: Optional[list["Block"]] = None


class ParagraphBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: Optional[list["Block"]] = None


class PdfBlock(BaseModel):
    caption: list[RichTextObject] = []
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None


class QuoteBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: Optional[list["Block"]] = None


class SyncedFromObject(BaseModel):
    type: Literal["block_id"]
    block_id: str


class SyncedBlock(BaseModel):
    synced_from: Optional[SyncedFromObject] = (
        None  # None for original, object for duplicate
    )
    children: Optional[list["Block"]] = None


class TableBlock(BaseModel):
    table_width: int
    has_column_header: bool = False
    has_row_header: bool = False


class TableRowBlock(BaseModel):
    cells: list[list[RichTextObject]]


class TableOfContentsBlock(BaseModel):
    color: BlockColor = "default"


class TemplateBlock(BaseModel):
    rich_text: list[RichTextObject]
    children: Optional[list["Block"]] = None


class ToDoBlock(BaseModel):
    rich_text: list[RichTextObject]
    checked: bool = False
    color: BlockColor = "default"
    children: Optional[list["Block"]] = None


class ToggleBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: Optional[list["Block"]] = None


class VideoBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: Optional[list[RichTextObject]] = None


class UnsupportedBlock(BaseModel):
    pass


# ============================================================================
# MAIN BLOCK MODEL
# ============================================================================


class Block(BaseModel):
    object: Literal["block"]
    id: str
    parent: Optional[ParentObject] = None
    type: BlockType
    created_time: str
    last_edited_time: str
    created_by: PartialUser
    last_edited_by: PartialUser
    archived: bool = False
    in_trash: bool = False
    has_children: bool = False

    # Block type-specific content (only one will be populated based on type)
    audio: Optional[AudioBlock] = None
    bookmark: Optional[BookmarkBlock] = None
    breadcrumb: Optional[BreadcrumbBlock] = None
    bulleted_list_item: Optional[BulletedListItemBlock] = None
    callout: Optional[CalloutBlock] = None
    child_database: Optional[ChildDatabaseBlock] = None
    child_page: Optional[ChildPageBlock] = None
    code: Optional[CodeBlock] = None
    column_list: Optional[ColumnListBlock] = None
    column: Optional[ColumnBlock] = None
    divider: Optional[DividerBlock] = None
    embed: Optional[EmbedBlock] = None
    equation: Optional[EquationBlock] = None
    file: Optional[FileBlock] = None
    heading_1: Optional[HeadingBlock] = None
    heading_2: Optional[HeadingBlock] = None
    heading_3: Optional[HeadingBlock] = None
    image: Optional[ImageBlock] = None
    link_preview: Optional[LinkPreviewBlock] = None
    link_to_page: Optional[LinkToPageBlock] = None
    numbered_list_item: Optional[NumberedListItemBlock] = None
    paragraph: Optional[ParagraphBlock] = None
    pdf: Optional[PdfBlock] = None
    quote: Optional[QuoteBlock] = None
    synced_block: Optional[SyncedBlock] = None
    table: Optional[TableBlock] = None
    table_row: Optional[TableRowBlock] = None
    table_of_contents: Optional[TableOfContentsBlock] = None
    template: Optional[TemplateBlock] = None
    to_do: Optional[ToDoBlock] = None
    toggle: Optional[ToggleBlock] = None
    video: Optional[VideoBlock] = None
    unsupported: Optional[UnsupportedBlock] = None

    def get_block_content(self) -> Optional[Any]:
        """Get the content object for this block based on its type."""
        return getattr(self, self.type, None)


# Forward reference resolution
Block.model_rebuild()
BulletedListItemBlock.model_rebuild()
CalloutBlock.model_rebuild()
HeadingBlock.model_rebuild()
NumberedListItemBlock.model_rebuild()
ParagraphBlock.model_rebuild()
QuoteBlock.model_rebuild()
SyncedBlock.model_rebuild()
TemplateBlock.model_rebuild()
ToDoBlock.model_rebuild()
ToggleBlock.model_rebuild()


# ============================================================================
# API REQUEST/RESPONSE MODELS
# ============================================================================


class BlockChildrenResponse(BaseModel):
    object: Literal["list"]
    results: list[Block]
    next_cursor: Optional[str] = None
    has_more: bool
    type: Literal["block"]
    block: Dict = {}
    request_id: str


class AppendBlockChildrenRequest(BaseModel):
    children: list[Dict[str, Any]]  # Block creation objects
    after: Optional[str] = None


class UpdateBlockRequest(BaseModel):
    # Type-specific updates based on block type
    # This would contain the block-specific content to update
    pass


class BlockResponse(BaseModel):
    """Single block response from the API"""

    object: Literal["block"]
    id: str
    parent: Optional[ParentObject] = None
    type: BlockType
    created_time: str
    last_edited_time: str
    created_by: PartialUser
    last_edited_by: PartialUser
    archived: bool = False
    in_trash: bool = False
    has_children: bool = False
    request_id: str

    # Block type-specific content
    audio: Optional[AudioBlock] = None
    bookmark: Optional[BookmarkBlock] = None
    breadcrumb: Optional[BreadcrumbBlock] = None
    bulleted_list_item: Optional[BulletedListItemBlock] = None
    callout: Optional[CalloutBlock] = None
    child_database: Optional[ChildDatabaseBlock] = None
    child_page: Optional[ChildPageBlock] = None
    code: Optional[CodeBlock] = None
    column_list: Optional[ColumnListBlock] = None
    column: Optional[ColumnBlock] = None
    divider: Optional[DividerBlock] = None
    embed: Optional[EmbedBlock] = None
    equation: Optional[EquationBlock] = None
    file: Optional[FileBlock] = None
    heading_1: Optional[HeadingBlock] = None
    heading_2: Optional[HeadingBlock] = None
    heading_3: Optional[HeadingBlock] = None
    image: Optional[ImageBlock] = None
    link_preview: Optional[LinkPreviewBlock] = None
    link_to_page: Optional[LinkToPageBlock] = None
    numbered_list_item: Optional[NumberedListItemBlock] = None
    paragraph: Optional[ParagraphBlock] = None
    pdf: Optional[PdfBlock] = None
    quote: Optional[QuoteBlock] = None
    synced_block: Optional[SyncedBlock] = None
    table: Optional[TableBlock] = None
    table_row: Optional[TableRowBlock] = None
    table_of_contents: Optional[TableOfContentsBlock] = None
    template: Optional[TemplateBlock] = None
    to_do: Optional[ToDoBlock] = None
    toggle: Optional[ToggleBlock] = None
    video: Optional[VideoBlock] = None
    unsupported: Optional[UnsupportedBlock] = None
