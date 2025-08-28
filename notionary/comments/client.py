from __future__ import annotations

from typing import AsyncGenerator, Optional

from notionary.base_notion_client import BaseNotionClient
from notionary.comments.models import Comment, CommentListResponse


class CommentClient(BaseNotionClient):
    """
    Client for Notion comment operations.
    Uses Pydantic models for typed responses.

    Notes / API constraints:
    - Listing returns only *unresolved* comments. Resolved comments are not returned.
    - You can create:
        1) a top-level comment on a page
        2) a reply in an existing discussion (requires discussion_id)
      You cannot start a brand-new inline thread via API.
    - Read/Insert comment capabilities must be enabled for the integration.
    """

    async def retrieve_comment(self, comment_id: str) -> Comment:
        """
        Retrieve a single Comment object by its ID.

        Requires the integration to have "Read comment" capability enabled.
        Raises 403 (restricted_resource) without it.
        """
        resp = await self.get(f"comments/{comment_id}")
        if resp is None:
            raise RuntimeError("Failed to retrieve comment.")
        return Comment.model_validate(resp)

    async def list_all_comments_for_page(
        self, *, page_id: str, page_size: int = 100
    ) -> list[Comment]:
        """Returns all unresolved comments for a page (handles pagination)."""
        results: list[Comment] = []
        cursor: str | None = None
        while True:
            page = await self.list_comments(
                block_id=page_id, start_cursor=cursor, page_size=page_size
            )
            results.extend(page.results)
            if not page.has_more:
                break
            cursor = page.next_cursor
        return results

    async def list_comments(
        self,
        *,
        block_id: str,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> CommentListResponse:
        """
        List unresolved comments for a page or block.

        Args:
            block_id: Page ID or block ID to list comments for.
            start_cursor: Pagination cursor.
            page_size: Max items per page (<= 100).

        Returns:
            CommentListResponse with results, next_cursor, has_more, etc.
        """
        params: dict[str, str | int] = {"block_id": block_id}
        if start_cursor:
            params["start_cursor"] = start_cursor
        if page_size:
            params["page_size"] = page_size

        resp = await self.get("comments", params=params)
        if resp is None:
            raise RuntimeError("Failed to list comments.")
        return CommentListResponse.model_validate(resp)

    async def iter_comments(
        self,
        *,
        block_id: str,
        page_size: int = 100,
    ) -> AsyncGenerator[Comment, None]:
        """
        Async generator over all unresolved comments for a given page/block.
        Handles pagination under the hood.
        """
        cursor: Optional[str] = None
        while True:
            page = await self.list_comments(
                block_id=block_id, start_cursor=cursor, page_size=page_size
            )
            for item in page.results:
                yield item
            if not page.has_more:
                break
            cursor = page.next_cursor

    async def create_comment_on_page(
        self,
        *,
        page_id: str,
        text: str,
        display_name: Optional[dict] = None,
        attachments: Optional[list[dict]] = None,
    ) -> Comment:
        """
        Create a top-level comment on a page.

        Args:
            page_id: Target page ID.
            text: Plain text content for the comment (rich_text will be constructed).
            display_name: Optional "Comment Display Name" object to override author label.
            attachments: Optional list of "Comment Attachment" objects (max 3).

        Returns:
            The created Comment object.
        """
        body: dict = {
            "parent": {"page_id": page_id},
            "rich_text": [{"type": "text", "text": {"content": text}}],
        }
        if display_name:
            body["display_name"] = display_name
        if attachments:
            body["attachments"] = attachments

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError("Failed to create page comment.")
        return Comment.model_validate(resp)

    async def reply_to_discussion(
        self,
        *,
        discussion_id: str,
        text: str,
        display_name: Optional[dict] = None,
        attachments: Optional[list[dict]] = None,
    ) -> Comment:
        """
        Reply to an existing discussion thread.

        Args:
            discussion_id: The discussion thread ID (obtain via list-comments or UI copy-link).
            text: Plain text content for the reply.
            display_name: Optional "Comment Display Name" object to override author label.
            attachments: Optional list of "Comment Attachment" objects (max 3).

        Returns:
            The created Comment object.
        """
        body: dict = {
            "discussion_id": discussion_id,
            "rich_text": [{"type": "text", "text": {"content": text}}],
        }
        if display_name:
            body["display_name"] = display_name
        if attachments:
            body["attachments"] = attachments

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError("Failed to reply to discussion.")
        return Comment.model_validate(resp)
