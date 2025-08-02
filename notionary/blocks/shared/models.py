from __future__ import annotations

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
    "to_do",
    "toggle",
    "unsupported",
    "video",
    "audio",
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


class LinkPreviewBlock(BaseModel):
    url: str


class LinkToPageBlock(BaseModel):
    type: Literal["page_id", "database_id"]
    page_id: Optional[str] = None
    database_id: Optional[str] = None



class UnsupportedBlock(BaseModel):
    pass


# ============================================================================
# MAIN BLOCK MODEL
# ============================================================================


class CreateUnsupportedBlock(BaseModel):
    type: Literal["unsupported"] = "unsupported"
    unsupported: UnsupportedBlock


# ============================================================================
# CREATE BLOCK UNION TYPE
# ============================================================================

# TODO: Nach Refactor muss diese Ding hier woanders hin basically
BlockCreateRequest = Union[
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
