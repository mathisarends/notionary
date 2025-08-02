from __future__ import annotations

from typing import Literal, Optional, Union, Any, Dict
from pydantic import BaseModel, Field


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
    "default_background",
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


class TextAnnotations(BaseModel):
    """Text formatting annotations"""

    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: str = "default"


class TextContent(BaseModel):
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


class ExternalUrl(BaseModel):
    url: str


class AudioContent(BaseModel):
    type: Literal["external"]
    external: ExternalUrl
    caption: list[RichTextObject] = Field(default_factory=list)


class AudioBlockCreate(BaseModel):
    type: Literal["audio"]
    audio: AudioContent


class AudioBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: list[RichTextObject] = Field(default_factory=list)


class BookmarkBlock(BaseModel):
    caption: list[RichTextObject] = Field(default_factory=list)
    url: str


class BreadcrumbBlock(BaseModel):
    pass


class BulletedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: list["Block"] = Field(default_factory=list)


class CalloutBlock(BaseModel):
    rich_text: list[RichTextObject]
    icon: Optional[IconObject] = None
    color: BlockColor = "default"
    children: list["Block"] = Field(default_factory=list)


class ChildDatabaseBlock(BaseModel):
    title: str


class ChildPageBlock(BaseModel):
    title: str


class CodeBlock(BaseModel):
    caption: list[RichTextObject] = Field(default_factory=list)
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
    caption: list[RichTextObject] = Field(default_factory=list)


class EquationBlock(BaseModel):
    expression: str


class FileBlock(BaseModel):
    caption: list[RichTextObject] = Field(default_factory=list)
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    name: Optional[str] = None


class HeadingBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    is_toggleable: bool = False
    children: list["Block"] = Field(default_factory=list)


class ImageBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: list[RichTextObject] = Field(default_factory=list)


class LinkPreviewBlock(BaseModel):
    url: str


class LinkToPageBlock(BaseModel):
    type: Literal["page_id", "database_id"]
    page_id: Optional[str] = None
    database_id: Optional[str] = None


class NumberedListItemBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: list["Block"] = Field(default_factory=list)


class ParagraphBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"


class PdfBlock(BaseModel):
    caption: list[RichTextObject] = Field(default_factory=list)
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None


class QuoteBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: list["Block"] = Field(default_factory=list)


class SyncedFromObject(BaseModel):
    type: Literal["block_id"]
    block_id: str


class SyncedBlock(BaseModel):
    synced_from: Optional[SyncedFromObject] = None  # None for original, object for duplicate
    children: list["Block"] = Field(default_factory=list)


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
    children: list["Block"] = Field(default_factory=list)


class ToDoBlock(BaseModel):
    rich_text: list[RichTextObject]
    checked: bool = False
    color: BlockColor = "default"
    children: list["Block"] = Field(default_factory=list)


class ToggleBlock(BaseModel):
    rich_text: list[RichTextObject]
    color: BlockColor = "default"
    children: list["Block"] = Field(default_factory=list)


class VideoBlock(BaseModel):
    type: Literal["external", "file", "file_upload"]
    external: Optional[ExternalFile] = None
    file: Optional[NotionHostedFile] = None
    file_upload: Optional[FileUploadFile] = None
    caption: list[RichTextObject] = Field(default_factory=list)


class UnsupportedBlock(BaseModel):
    pass


# ============================================================================
# MAIN BLOCK MODEL
# ============================================================================


class CreateAudioBlock(BaseModel):
    type: Literal["audio"] = "audio"
    audio: AudioBlock


class CreateBookmarkBlock(BaseModel):
    type: Literal["bookmark"] = "bookmark"
    bookmark: BookmarkBlock


class CreateBreadcrumbBlock(BaseModel):
    type: Literal["breadcrumb"] = "breadcrumb"
    breadcrumb: BreadcrumbBlock


class CreateBulletedListItemBlock(BaseModel):
    type: Literal["bulleted_list_item"] = "bulleted_list_item"
    bulleted_list_item: BulletedListItemBlock


class CreateCalloutBlock(BaseModel):
    type: Literal["callout"] = "callout"
    callout: CalloutBlock


class CreateChildDatabaseBlock(BaseModel):
    type: Literal["child_database"] = "child_database"
    child_database: ChildDatabaseBlock


class CreateChildPageBlock(BaseModel):
    type: Literal["child_page"] = "child_page"
    child_page: ChildPageBlock


class CreateCodeBlock(BaseModel):
    type: Literal["code"] = "code"
    code: CodeBlock


class CreateColumnListBlock(BaseModel):
    type: Literal["column_list"] = "column_list"
    column_list: ColumnListBlock


class CreateColumnBlock(BaseModel):
    type: Literal["column"] = "column"
    column: ColumnBlock


class CreateDividerBlock(BaseModel):
    type: Literal["divider"] = "divider"
    divider: DividerBlock


class CreateEmbedBlock(BaseModel):
    type: Literal["embed"] = "embed"
    embed: EmbedBlock


class CreateEquationBlock(BaseModel):
    type: Literal["equation"] = "equation"
    equation: EquationBlock


class CreateFileBlock(BaseModel):
    type: Literal["file"] = "file"
    file: FileBlock


class CreateHeading1Block(BaseModel):
    type: Literal["heading_1"] = "heading_1"
    heading_1: HeadingBlock


class CreateHeading2Block(BaseModel):
    type: Literal["heading_2"] = "heading_2"
    heading_2: HeadingBlock


class CreateHeading3Block(BaseModel):
    type: Literal["heading_3"] = "heading_3"
    heading_3: HeadingBlock


class CreateImageBlock(BaseModel):
    type: Literal["image"] = "image"
    image: ImageBlock


class CreateLinkPreviewBlock(BaseModel):
    type: Literal["link_preview"] = "link_preview"
    link_preview: LinkPreviewBlock


class CreateLinkToPageBlock(BaseModel):
    type: Literal["link_to_page"] = "link_to_page"
    link_to_page: LinkToPageBlock


class CreateNumberedListItemBlock(BaseModel):
    type: Literal["numbered_list_item"] = "numbered_list_item"
    numbered_list_item: NumberedListItemBlock


class CreateParagraphBlock(BaseModel):
    type: Literal["paragraph"] = "paragraph"
    paragraph: ParagraphBlock


class CreatePdfBlock(BaseModel):
    type: Literal["pdf"] = "pdf"
    pdf: PdfBlock


class CreateQuoteBlock(BaseModel):
    type: Literal["quote"] = "quote"
    quote: QuoteBlock


class CreateSyncedBlock(BaseModel):
    type: Literal["synced_block"] = "synced_block"
    synced_block: SyncedBlock


class CreateTableBlock(BaseModel):
    type: Literal["table"] = "table"
    table: TableBlock


class CreateTableRowBlock(BaseModel):
    type: Literal["table_row"] = "table_row"
    table_row: TableRowBlock


class CreateTableOfContentsBlock(BaseModel):
    type: Literal["table_of_contents"] = "table_of_contents"
    table_of_contents: TableOfContentsBlock


class CreateTemplateBlock(BaseModel):
    type: Literal["template"] = "template"
    template: TemplateBlock


class CreateToDoBlock(BaseModel):
    type: Literal["to_do"] = "to_do"
    to_do: ToDoBlock


class CreateToggleBlock(BaseModel):
    type: Literal["toggle"] = "toggle"
    toggle: ToggleBlock


class CreateVideoBlock(BaseModel):
    type: Literal["video"] = "video"
    video: VideoBlock


class CreateUnsupportedBlock(BaseModel):
    type: Literal["unsupported"] = "unsupported"
    unsupported: UnsupportedBlock


# ============================================================================
# CREATE BLOCK UNION TYPE
# ============================================================================

BlockCreateRequest = Union[
    CreateAudioBlock,
    CreateBookmarkBlock,
    CreateBreadcrumbBlock,
    CreateBulletedListItemBlock,
    CreateCalloutBlock,
    CreateChildDatabaseBlock,
    CreateChildPageBlock,
    CreateCodeBlock,
    CreateColumnListBlock,
    CreateColumnBlock,
    CreateDividerBlock,
    CreateEmbedBlock,
    CreateEquationBlock,
    CreateFileBlock,
    CreateHeading1Block,
    CreateHeading2Block,
    CreateHeading3Block,
    CreateImageBlock,
    CreateLinkPreviewBlock,
    CreateLinkToPageBlock,
    CreateNumberedListItemBlock,
    CreateParagraphBlock,
    CreatePdfBlock,
    CreateQuoteBlock,
    CreateSyncedBlock,
    CreateTableBlock,
    CreateTableRowBlock,
    CreateTableOfContentsBlock,
    CreateTemplateBlock,
    CreateToDoBlock,
    CreateToggleBlock,
    CreateVideoBlock,
    CreateUnsupportedBlock,
]


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

    children: Optional[list[Block]] = None  # for recursive structure

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
