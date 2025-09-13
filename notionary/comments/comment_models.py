# notionary/comments/models.py
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict

from notionary.blocks.rich_text import RichTextObject


class UserRef(BaseModel):
    """Minimal Notion user reference."""

    model_config = ConfigDict(extra="ignore")
    object: Literal["user"] = "user"
    id: str


class CommentParent(BaseModel):
    """
    Parent of a comment. Can be page_id or block_id.
    Notion responds with the active one; the other remains None.
    """

    model_config = ConfigDict(extra="ignore")
    type: Literal["page_id", "block_id"]
    page_id: Optional[str] = None
    block_id: Optional[str] = None


class FileWithExpiry(BaseModel):
    """File object with temporary URL (common Notion pattern)."""

    model_config = ConfigDict(extra="ignore")
    url: str
    expiry_time: Optional[datetime] = None


class CommentAttachmentFile(BaseModel):
    """Attachment stored by Notion with expiring download URL."""

    model_config = ConfigDict(extra="ignore")
    type: Literal["file"] = "file"
    name: Optional[str] = None
    file: FileWithExpiry


class CommentAttachmentExternal(BaseModel):
    """External attachment referenced by URL."""

    model_config = ConfigDict(extra="ignore")
    type: Literal["external"] = "external"
    name: Optional[str] = None
    external: dict  # {"url": "..."} – kept generic


CommentAttachment = Union[CommentAttachmentFile, CommentAttachmentExternal]


# ---------------------------
# Display name override (optional)
# ---------------------------


class CommentDisplayName(BaseModel):
    """
    Optional display name override for comments created by an integration.
    Example: {"type": "integration", "resolved_name": "int"}.
    """

    model_config = ConfigDict(extra="ignore")
    type: str
    resolved_name: Optional[str] = None


# ---------------------------
# Core Comment object
# ---------------------------


class Comment(BaseModel):
    """
    Notion Comment object as returned by:
      - GET /v1/comments/{comment_id} (retrieve)
      - GET /v1/comments?block_id=... (list -> in results[])
      - POST /v1/comments (create)
    """

    model_config = ConfigDict(extra="ignore")

    object: Literal["comment"] = "comment"
    id: str

    parent: CommentParent
    discussion_id: str

    created_time: datetime
    last_edited_time: datetime

    created_by: UserRef

    rich_text: list[RichTextObject] = Field(default_factory=list)

    # Optional fields that may appear depending on capabilities/payload
    display_name: Optional[CommentDisplayName] = None
    attachments: Optional[list[CommentAttachment]] = None


# ---------------------------
# List envelope (for list-comments)
# ---------------------------


class CommentListResponse(BaseModel):
    """
    Envelope for GET /v1/comments?block_id=...
    """

    model_config = ConfigDict(extra="ignore")

    object: Literal["list"] = "list"
    results: list[Comment] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    has_more: bool = False

    # Notion includes these two fields on the list envelope.
    type: Optional[Literal["comment"]] = None
    comment: Optional[dict] = None
