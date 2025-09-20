from __future__ import annotations

from typing import AsyncGenerator, Optional

from notionary.http_client import NotionHttpClient
from notionary.comments.comment_models import (
    Comment,
    CommentListResponse,
    CommentDisplayName,
    CommentAttachment,
    CommentCreateRequest,
    CommentListRequest,
)
from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter


class CommentClient(NotionHttpClient):
    """
    Client for Notion comment operations.
    """

    async def list_all_comments_for_page(
        self, page_id: str, *, page_size: int = 100
    ) -> list[Comment]:
        """
        Returns all unresolved comments for a page (handles pagination automatically).

        Args:
            page_id: Page ID to get comments for.
            page_size: Items per page for pagination (default: 100).
        """
        results: list[Comment] = []
        cursor: str | None = None

        while True:
            page = await self._list_comments(
                page_id, start_cursor=cursor, page_size=page_size
            )
            results.extend(page.results)
            if not page.has_more:
                break
            cursor = page.next_cursor

        return results

    async def iter_comments(
        self,
        block_id: str,
        *,
        page_size: int = 100,
    ) -> AsyncGenerator[Comment, None]:
        """
        Async generator over all unresolved comments for a given page/block.
        Handles pagination automatically.

        Args:
            block_id: Page ID or block ID to iterate comments for.
            page_size: Items per page for pagination (default: 100).

        Yields:
            Individual Comment objects.
        """
        cursor: Optional[str] = None

        while True:
            page = await self._list_comments(
                block_id, start_cursor=cursor, page_size=page_size
            )
            for item in page.results:
                yield item
            if not page.has_more:
                break
            cursor = page.next_cursor

    async def create_comment(
        self,
        rich_text_str: str,
        *,
        page_id: Optional[str] = None,
        discussion_id: Optional[str] = None,
        attachments: Optional[list[CommentAttachment]] = None,
    ) -> Comment:
        """
        Create a comment on a page OR reply to an existing discussion.

        Args:
            rich_text_str: Plain text content (will be converted to rich text).
            page_id: Page ID to comment on (for top-level comments).
            discussion_id: Discussion ID to reply to (for replies).
            attachments: Optional list of attachments (max 3).
        """
        if (page_id is None) == (discussion_id is None):
            raise ValueError("Specify exactly one parent: page_id OR discussion_id")

        # Convert plain text to rich text
        rich_text = await TextInlineFormatter.parse_inline_formatting(rich_text_str)

        if page_id:
            request = CommentCreateRequest.for_page(
                page_id=page_id,
                rich_text=rich_text,
                attachments=attachments,
            )
        else:
            request = CommentCreateRequest.for_discussion(
                discussion_id=discussion_id,
                rich_text=rich_text,
                attachments=attachments,
            )

        # Convert request to API format and make the call
        body = request.model_dump(exclude_unset=True, exclude_none=True)

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError(
                "Failed to create comment - check logs for HTTP error details."
            )

        return Comment.model_validate(resp)

    async def create_comment_on_page(
        self,
        page_id: str,
        text: str,
        *,
        display_name: Optional[CommentDisplayName] = None,
        attachments: Optional[list[CommentAttachment]] = None,
    ) -> Comment:
        """
        Create a top-level comment on a page using plain text.

        Args:
            page_id: Target page ID.
            text: Plain text content.
            display_name: Optional display name override.
            attachments: Optional list of attachments (max 3).
        """
        return await self.create_comment(
            text,
            page_id=page_id,
            display_name=display_name,
            attachments=attachments,
        )

    async def reply_to_discussion(
        self,
        discussion_id: str,
        text: str,
        *,
        display_name: Optional[CommentDisplayName] = None,
        attachments: Optional[list[CommentAttachment]] = None,
    ) -> Comment:
        """
        Reply to an existing discussion using plain text.

        Args:
            discussion_id: Target discussion ID to reply to.
            text: Plain text content.
            display_name: Optional display name override.
            attachments: Optional list of attachments (max 3).
        """
        return await self.create_comment(
            text,
            discussion_id=discussion_id,
            display_name=display_name,
            attachments=attachments,
        )

    async def _list_comments(
        self,
        block_id: str,
        *,
        start_cursor: Optional[str] = None,
        page_size: int = 100,
    ) -> CommentListResponse:
        """
        List unresolved comments for a page or block.

        Args:
            block_id: Page ID or block ID to list comments for.
            start_cursor: Pagination cursor.
            page_size: Max items per page (<= 100).
        """
        request = CommentListRequest(
            block_id=block_id,
            start_cursor=start_cursor,
            page_size=page_size,
        )
        resp = await self.get("comments", params=request.to_params())
        if resp is None:
            raise RuntimeError("Failed to list comments.")
        return CommentListResponse.model_validate(resp)
