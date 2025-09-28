from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from notionary.blocks.rich_text.rich_text_models import RichTextObject


class UserRef(BaseModel):
    """Minimal Notion user reference."""

    model_config = ConfigDict(extra="ignore")
    object: Literal["user"] = "user"
    id: str


class CommentParent(BaseModel):
    """
    Parent of a CommentDto. Can be page_id or block_id.
    Notion responds with the active one; the other remains None.
    """

    model_config = ConfigDict(extra="ignore")
    type: Literal["page_id", "block_id"]
    page_id: str | None = None
    block_id: str | None = None


class FileWithExpiry(BaseModel):
    """File object with temporary URL (common Notion pattern)."""

    model_config = ConfigDict(extra="ignore")
    url: str
    expiry_time: datetime | None = None


class CommentAttachmentFile(BaseModel):
    """Attachment stored by Notion with expiring download URL."""

    model_config = ConfigDict(extra="ignore")
    type: Literal["file"] = "file"
    name: str | None = None
    file: FileWithExpiry


class CommentAttachmentExternal(BaseModel):
    """External attachment referenced by URL."""

    model_config = ConfigDict(extra="ignore")
    type: Literal["external"] = "external"
    name: str | None = None
    external: dict


CommentAttachment = CommentAttachmentFile | CommentAttachmentExternal


# ---------------------------
# Display name override (optional)
# ---------------------------


class CommentDisplayName(BaseModel):
    """
    Optional display name override for comments created by an integration.
    Example: {"type": "integration", "resolved_name": "int"}.
    """

    model_config = ConfigDict(extra="ignore")
    type: Literal["integration"] = "integration"
    resolved_name: str | None = None

    @classmethod
    def for_integration(cls, name: str | None = None) -> CommentDisplayName:
        """
        Create a CommentDisplayName for an integration with a custom name.
        """
        return cls(type="integration", resolved_name=name)


# ---------------------------
# Request models for creating comments
# ---------------------------


class CommentCreateRequest(BaseModel):
    """
    Request model for creating a CommentDto.
    Handles both page comments and discussion replies.
    """

    model_config = ConfigDict(extra="ignore")

    rich_text: list[RichTextObject]
    parent: CommentParent | None = None
    discussion_id: str | None = None
    display_name: CommentDisplayName | None = None
    attachments: list[CommentAttachment] | None = None

    @classmethod
    def for_page(
        cls,
        page_id: str,
        rich_text: list[RichTextObject],
        display_name: CommentDisplayName | None = None,
        attachments: list[CommentAttachment] | None = None,
    ) -> CommentCreateRequest:
        """Create a request for a page CommentDto."""
        return cls(
            rich_text=rich_text,
            parent=CommentParent(type="page_id", page_id=page_id),
            display_name=display_name,
            attachments=attachments,
        )

    @classmethod
    def for_discussion(
        cls,
        discussion_id: str,
        rich_text: list[RichTextObject],
        display_name: CommentDisplayName | None = None,
        attachments: list[CommentAttachment] | None = None,
    ) -> CommentCreateRequest:
        """Create a request for a discussion reply."""
        return cls(
            rich_text=rich_text,
            discussion_id=discussion_id,
            display_name=display_name,
            attachments=attachments,
        )


class CommentListRequest(BaseModel):
    """
    Request model for listing comments.
    """

    model_config = ConfigDict(extra="ignore")

    block_id: str
    start_cursor: str | None = None
    page_size: int | None = None

    def to_params(self) -> dict[str, str | int]:
        """Convert to query parameters for the API request."""
        params: dict[str, str | int] = {"block_id": self.block_id}
        if self.start_cursor:
            params["start_cursor"] = self.start_cursor
        if self.page_size:
            params["page_size"] = self.page_size
        return params


# ---------------------------
# Core CommentDto object
# ---------------------------


class CommentDto(BaseModel):
    object: Literal["comment"] = "comment"
    id: str

    parent: CommentParent
    discussion_id: str

    created_time: datetime
    last_edited_time: datetime

    created_by: UserRef

    rich_text: list[RichTextObject] = Field(default_factory=list)

    # Optional fields that may appear depending on capabilities/payload
    display_name: CommentDisplayName | None = None
    attachments: list[CommentAttachment] | None = None


# ---------------------------
# List envelope (for list-comments)
# ---------------------------


class CommentListResponse(BaseModel):
    object: Literal["list"] = "list"
    results: list[CommentDto] = Field(default_factory=list)
    next_cursor: str | None = None
    has_more: bool = False
