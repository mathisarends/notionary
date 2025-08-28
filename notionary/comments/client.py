from __future__ import annotations

from typing import Any, AsyncGenerator, Optional

from notionary.base_notion_client import BaseNotionClient
from notionary.blocks.rich_text.rich_text_models import RichTextObject
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

    async def create_comment(
        self,
        *,
        page_id: Optional[str] = None,
        discussion_id: Optional[str] = None,
        content: Optional[str] = None,
        rich_text: Optional[list[RichTextObject]] = None,
        display_name: Optional[dict[str, Any]] = None,
        attachments: Optional[list[dict[str, Any]]] = None,
    ) -> Comment:
        """
        Create a comment on a page OR reply to an existing discussion.

        Rules:
        - Exactly one of page_id or discussion_id must be provided.
        - Provide either rich_text OR content (plain text). If both given, rich_text wins.
        - Up to 3 attachments allowed by Notion.
        """
        # validate parent
        if (page_id is None) == (discussion_id is None):
            raise ValueError("Specify exactly one parent: page_id OR discussion_id")

        # build rich_text if only content is provided
        rt = rich_text if rich_text else None
        if rt is None:
            if not content:
                raise ValueError("Provide either 'rich_text' or 'content'.")
            rt = [{"type": "text", "text": {"content": content}}]

        body: dict[str, Any] = {"rich_text": rt}
        if page_id:
            body["parent"] = {"page_id": page_id}
        else:
            body["discussion_id"] = discussion_id

        if display_name:
            body["display_name"] = display_name
        if attachments:
            body["attachments"] = attachments

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError("Failed to create comment.")
        return Comment.model_validate(resp)

    # ---------- Convenience wrappers ----------

    async def create_comment_on_page(
        self,
        *,
        page_id: str,
        text: str,
        display_name: Optional[dict] = None,
        attachments: Optional[list[dict]] = None,
    ) -> Comment:
        return await self.create_comment(
            page_id=page_id,
            content=text,
            display_name=display_name,
            attachments=attachments,
        )

    async def reply_to_discussion(
        self,
        *,
        discussion_id: str,
        text: str,
        display_name: Optional[dict] = None,
        attachments: Optional[list[dict]] = None,
    ) -> Comment:
        return await self.create_comment(
            discussion_id=discussion_id,
            content=text,
            display_name=display_name,
            attachments=attachments,
        )