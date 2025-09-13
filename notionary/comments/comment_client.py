from __future__ import annotations

from typing import Any, AsyncGenerator, Optional

from notionary.base_notion_client import BaseNotionClient
from notionary.blocks.rich_text.rich_text_models import RichTextObject
from notionary.comments.comment_models import Comment, CommentListResponse


class CommentClient(BaseNotionClient):
    """
    Client for Notion comment operations.
    """

    async def retrieve_comment(self, comment_id: str) -> Comment:
        """
        Retrieve a single Comment object by its ID.
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

    async def create_comment(
        self,
        rich_text: list[RichTextObject],
        *,
        page_id: Optional[str] = None,
        discussion_id: Optional[str] = None,
        display_name: Optional[dict[str, Any]] = None,
        attachments: Optional[list[dict[str, Any]]] = None,
    ) -> Comment:
        """
        Create a comment on a page OR reply to an existing discussion.
        Follows the exact schema from Notion API documentation.
        """
        # Validate that exactly one parent is provided
        if (page_id is None) == (discussion_id is None):
            raise ValueError("Specify exactly one parent: page_id OR discussion_id")

        # Build rich_text according to API schema - only include necessary fields
        rich_text_dicts = []
        for obj in rich_text:
            obj_dict = obj.model_dump(exclude_none=True)
            
            # Build minimal rich_text object following API schema
            api_rich_text = {
                "type": obj_dict["type"]
            }
            
            # Add type-specific content
            if obj_dict["type"] == "text" and "text" in obj_dict:
                api_rich_text["text"] = {
                    "content": obj_dict["text"]["content"]
                }
                # Only add link if it exists and is not None
                if obj_dict["text"].get("link"):
                    api_rich_text["text"]["link"] = obj_dict["text"]["link"]
            
            elif obj_dict["type"] == "mention" and "mention" in obj_dict:
                api_rich_text["mention"] = obj_dict["mention"]
            
            elif obj_dict["type"] == "equation" and "equation" in obj_dict:
                api_rich_text["equation"] = obj_dict["equation"]
            
            # Add annotations if they exist (API docs show this is included)
            if "annotations" in obj_dict:
                api_rich_text["annotations"] = obj_dict["annotations"]
            
            rich_text_dicts.append(api_rich_text)

        # Build request body according to API schema
        body: dict[str, Any] = {
            "rich_text": rich_text_dicts
        }
        
        # Add parent - exactly as shown in API docs
        if page_id:
            body["parent"] = {
                "type": "page_id", 
                "page_id": page_id
            }
        else:
            body["discussion_id"] = discussion_id

        # Add optional fields only if provided
        if display_name:
            body["display_name"] = display_name
        if attachments:
            body["attachments"] = attachments

        import json
        print(f"Creating comment with API-compliant body: {json.dumps(body, indent=2)}")

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError("Failed to create comment - check logs for HTTP error details.")
        
        return Comment.model_validate(resp)


    # ---------- Convenience wrappers ----------

    async def create_comment_on_page(
        self,
        *,
        page_id: str,
        text: str,
        attachments: Optional[list[dict]] = None,
    ) -> Comment:
        """Create a top-level comment on a page using plain text."""
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        # Convert plain text to rich text
        rich_text = await TextInlineFormatter.parse_inline_formatting(text)

        return await self.create_comment(
            rich_text,
            page_id=page_id,
            attachments=attachments,
        )

    async def reply_to_discussion(
        self,
        *,
        discussion_id: str,
        text: str,
        attachments: Optional[list[dict]] = None,
    ) -> Comment:
        """Reply to an existing discussion using plain text."""
        from notionary.blocks.rich_text.text_inline_formatter import TextInlineFormatter

        # Convert plain text to rich text
        rich_text = await TextInlineFormatter.parse_inline_formatting(text)

        return await self.create_comment(
            rich_text,
            discussion_id=discussion_id,
            attachments=attachments,
        )
