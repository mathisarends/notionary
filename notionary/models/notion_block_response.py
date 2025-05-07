from typing import List, Optional, Union, Literal
from pydantic import BaseModel


# Rich Text Komponenten
class TextContent(BaseModel):
    content: str
    link: Optional[dict] = None


class Annotations(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str


class RichText(BaseModel):
    type: Literal["text"]
    text: TextContent
    annotations: Annotations
    plain_text: str
    href: Optional[str]


# Benutzerobjekt
class User(BaseModel):
    object: str
    id: str


# Elternobjekte
class PageParent(BaseModel):
    type: Literal["page_id"]
    page_id: str


class DatabaseParent(BaseModel):
    type: Literal["database_id"]
    database_id: str


class WorkspaceParent(BaseModel):
    type: Literal["workspace"]
    workspace: bool = True


Parent = Union[PageParent, DatabaseParent, WorkspaceParent]


# Block-spezifische Inhalte
class ParagraphBlock(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"


class Heading1Block(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"
    is_toggleable: Optional[bool] = False


class Heading2Block(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"
    is_toggleable: Optional[bool] = False


class Heading3Block(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"
    is_toggleable: Optional[bool] = False


class BulletedListItemBlock(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"


class NumberedListItemBlock(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"


class ToDoBlock(BaseModel):
    rich_text: List[RichText]
    checked: Optional[bool] = False
    color: Optional[str] = "default"


class ToggleBlock(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"


class QuoteBlock(BaseModel):
    rich_text: List[RichText]
    color: Optional[str] = "default"


class CalloutBlock(BaseModel):
    rich_text: List[RichText]
    icon: Optional[dict] = None
    color: Optional[str] = "default"


class CodeBlock(BaseModel):
    rich_text: List[RichText]
    language: Optional[str] = "plain text"


class EquationBlock(BaseModel):
    expression: str


class DividerBlock(BaseModel):
    pass


class TableOfContentsBlock(BaseModel):
    color: Optional[str] = "default"


class BreadcrumbBlock(BaseModel):
    pass


class ColumnListBlock(BaseModel):
    pass


class ColumnBlock(BaseModel):
    pass


class LinkToPageBlock(BaseModel):
    type: str
    page_id: Optional[str] = None
    database_id: Optional[str] = None


class SyncedBlock(BaseModel):
    synced_from: Optional[dict] = None


class TemplateBlock(BaseModel):
    rich_text: List[RichText]


class TableBlock(BaseModel):
    table_width: int
    has_column_header: bool
    has_row_header: bool


class TableRowBlock(BaseModel):
    cells: List[List[RichText]]


class BookmarkBlock(BaseModel):
    caption: List[RichText]
    url: str


class EmbedBlock(BaseModel):
    url: str


class ImageBlock(BaseModel):
    type: str
    external: Optional[dict] = None
    file: Optional[dict] = None
    caption: List[RichText]


class VideoBlock(BaseModel):
    type: str
    external: Optional[dict] = None
    file: Optional[dict] = None
    caption: List[RichText]


class PDFBlock(BaseModel):
    type: str
    external: Optional[dict] = None
    file: Optional[dict] = None
    caption: List[RichText]


class FileBlock(BaseModel):
    type: str
    external: Optional[dict] = None
    file: Optional[dict] = None
    caption: List[RichText]


class AudioBlock(BaseModel):
    type: str
    external: Optional[dict] = None
    file: Optional[dict] = None
    caption: List[RichText]


class LinkPreviewBlock(BaseModel):
    url: str


class ChildPageBlock(BaseModel):
    title: str


class ChildDatabaseBlock(BaseModel):
    title: str


# TODO: Use the block typing here:
# Test the code base.
class Block(BaseModel):
    object: Literal["block"]
    id: str
    parent: Parent
    created_time: str
    last_edited_time: str
    created_by: User
    last_edited_by: User
    has_children: bool
    archived: bool
    in_trash: bool
    type: str
    paragraph: Optional[ParagraphBlock] = None
    heading_1: Optional[Heading1Block] = None
    heading_2: Optional[Heading2Block] = None
    heading_3: Optional[Heading3Block] = None
    bulleted_list_item: Optional[BulletedListItemBlock] = None
    numbered_list_item: Optional[NumberedListItemBlock] = None
    to_do: Optional[ToDoBlock] = None
    toggle: Optional[ToggleBlock] = None
    quote: Optional[QuoteBlock] = None
    callout: Optional[CalloutBlock] = None
    code: Optional[CodeBlock] = None
    equation: Optional[EquationBlock] = None
    divider: Optional[DividerBlock] = None
    table_of_contents: Optional[TableOfContentsBlock] = None
    breadcrumb: Optional[BreadcrumbBlock] = None
    column_list: Optional[ColumnListBlock] = None
    column: Optional[ColumnBlock] = None
    link_to_page: Optional[LinkToPageBlock] = None
    synced_block: Optional[SyncedBlock] = None
    template: Optional[TemplateBlock] = None
    table: Optional[TableBlock] = None
    table_row: Optional[TableRowBlock] = None
    bookmark: Optional[BookmarkBlock] = None
    embed: Optional[EmbedBlock] = None
    image: Optional[ImageBlock] = None
    video: Optional[VideoBlock] = None
    pdf: Optional[PDFBlock] = None
    file: Optional[FileBlock] = None
    audio: Optional[AudioBlock] = None
    link_preview: Optional[LinkPreviewBlock] = None
    child_page: Optional[ChildPageBlock] = None
    child_database: Optional[ChildDatabaseBlock] = None
    unsupported: Optional[dict] = None
