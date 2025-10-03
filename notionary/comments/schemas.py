from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from notionary.blocks.mappings.rich_text.models import RichText

# ---------------------------
# Comment Parent
# ---------------------------


class CommentParentType(StrEnum):
    PAGE_ID = "page_id"
    BLOCK_ID = "block_id"


class PageCommentParent(BaseModel):
    type: Literal[CommentParentType.PAGE_ID] = CommentParentType.PAGE_ID
    page_id: str


class BlockCommentParent(BaseModel):
    type: Literal[CommentParentType.BLOCK_ID] = CommentParentType.BLOCK_ID
    block_id: str


CommentParent = PageCommentParent | BlockCommentParent


# ---------------------------
# Comment Attachment (Response/DTO)
# ---------------------------


class CommentAttachmentCategory(StrEnum):
    AUDIO = "audio"
    IMAGE = "image"
    PDF = "pdf"
    PRODUCTIVITY = "productivity"
    VIDEO = "video"


class FileWithExpiry(BaseModel):
    url: str
    expiry_time: datetime


class CommentAttachmentDto(BaseModel):
    category: CommentAttachmentCategory
    file: FileWithExpiry


# ---------------------------
# Comment Attachment (Request/Input)
# ---------------------------


class CommentAttachmentFileUploadType(StrEnum):
    FILE_UPLOAD = "file_upload"


class CommentAttachmentInput(BaseModel):
    file_upload_id: str
    type: Literal[CommentAttachmentFileUploadType.FILE_UPLOAD] = CommentAttachmentFileUploadType.FILE_UPLOAD


# ---------------------------
# Comment Display Name
# ---------------------------


class CommentDisplayNameType(StrEnum):
    INTEGRATION = "integration"
    USER = "user"
    CUSTOM = "custom"


class CustomDisplayName(BaseModel):
    name: str


class IntegrationDisplayName(BaseModel):
    type: Literal[CommentDisplayNameType.INTEGRATION] = CommentDisplayNameType.INTEGRATION


class UserDisplayName(BaseModel):
    type: Literal[CommentDisplayNameType.USER] = CommentDisplayNameType.USER


class CustomCommentDisplayName(BaseModel):
    type: Literal[CommentDisplayNameType.CUSTOM] = CommentDisplayNameType.CUSTOM
    custom: CustomDisplayName


CommentDisplayNameInput = IntegrationDisplayName | UserDisplayName | CustomCommentDisplayName


class CommentDisplayNameDto(BaseModel):
    type: CommentDisplayNameType
    resolved_name: str


# ---------------------------
# Comment Create Request
# ---------------------------


class CommentCreateRequest(BaseModel):
    rich_text: list[RichText]
    parent: CommentParent | None = None
    discussion_id: str | None = None
    display_name: CommentDisplayNameInput | None = None
    attachments: list[CommentAttachmentInput] | None = None

    @classmethod
    def for_page(
        cls,
        page_id: str,
        rich_text: list[RichText],
        display_name: CommentDisplayNameInput | None = None,
        attachments: list[CommentAttachmentInput] | None = None,
    ) -> CommentCreateRequest:
        return cls(
            rich_text=rich_text,
            parent=PageCommentParent(page_id=page_id),
            display_name=display_name,
            attachments=attachments,
        )

    @classmethod
    def for_block(
        cls,
        block_id: str,
        rich_text: list[RichText],
        display_name: CommentDisplayNameInput | None = None,
        attachments: list[CommentAttachmentInput] | None = None,
    ) -> CommentCreateRequest:
        return cls(
            rich_text=rich_text,
            parent=BlockCommentParent(block_id=block_id),
            display_name=display_name,
            attachments=attachments,
        )

    @classmethod
    def for_discussion(
        cls,
        discussion_id: str,
        rich_text: list[RichText],
        display_name: CommentDisplayNameInput | None = None,
        attachments: list[CommentAttachmentInput] | None = None,
    ) -> CommentCreateRequest:
        return cls(
            rich_text=rich_text,
            discussion_id=discussion_id,
            display_name=display_name,
            attachments=attachments,
        )


# ---------------------------
# Comment List Request
# ---------------------------


class CommentListRequest(BaseModel):
    block_id: str
    start_cursor: str | None = None
    page_size: int | None = None

    def to_params(self) -> dict[str, str | int]:
        params: dict[str, str | int] = {"block_id": self.block_id}
        if self.start_cursor:
            params["start_cursor"] = self.start_cursor
        if self.page_size:
            params["page_size"] = self.page_size
        return params


# ---------------------------
# User Reference
# ---------------------------


class UserRef(BaseModel):
    object: Literal["user"] = "user"
    id: str


# ---------------------------
# Comment DTO (Response)
# ---------------------------


class CommentDto(BaseModel):
    """Comment object as returned by the API"""

    object: Literal["comment"] = "comment"
    id: str

    parent: CommentParent
    discussion_id: str

    created_time: datetime
    last_edited_time: datetime

    created_by: UserRef

    rich_text: list[RichText] = Field(default_factory=list)
    attachments: list[CommentAttachmentDto] = Field(default_factory=list)
    display_name: CommentDisplayNameDto | None = None


# ---------------------------
# List Response
# ---------------------------


class CommentListResponse(BaseModel):
    object: Literal["list"] = "list"
    results: list[CommentDto] = Field(default_factory=list)
    next_cursor: str | None = None
    has_more: bool = False


# ---------------------------
# Convenience Builders
# ---------------------------


class CommentDisplayNameBuilder:
    """Helper class to build display names easily"""

    @staticmethod
    def integration() -> IntegrationDisplayName:
        return IntegrationDisplayName()

    @staticmethod
    def user() -> UserDisplayName:
        return UserDisplayName()

    @staticmethod
    def custom(name: str) -> CustomCommentDisplayName:
        return CustomCommentDisplayName(custom=CustomDisplayName(name=name))
