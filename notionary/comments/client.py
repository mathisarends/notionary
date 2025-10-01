import asyncio
from collections.abc import AsyncGenerator

from notionary.blocks.rich_text.markdown_rich_text_converter import MarkdownRichTextConverter
from notionary.comments.factory import CommentFactory
from notionary.comments.models import Comment
from notionary.comments.schemas import (
    CommentCreateRequest,
    CommentDto,
    CommentListRequest,
    CommentListResponse,
)
from notionary.http.http_client import NotionHttpClient


class CommentClient(NotionHttpClient):
    def __init__(self, comment_factory: CommentFactory | None) -> None:
        super().__init__()
        self.comment = comment_factory or CommentFactory()

    async def list_all_comments_for_page(self, page_id: str, *, page_size: int = 100) -> list[Comment]:
        results: list[CommentDto] = []
        cursor: str | None = None

        while True:
            page = await self._list_comments(page_id, start_cursor=cursor, page_size=page_size)
            results.extend(page.results)
            if not page.has_more:
                break
            cursor = page.next_cursor

        comments = await asyncio.gather(*(self.comment_factory.create_from_dto(dto) for dto in results))

        return comments

    async def iter_comments(
        self,
        block_id: str,
        *,
        page_size: int = 100,
    ) -> AsyncGenerator[CommentDto]:
        cursor: str | None = None

        while True:
            page = await self._list_comments(block_id, start_cursor=cursor, page_size=page_size)
            for item in page.results:
                yield item
            if not page.has_more:
                break
            cursor = page.next_cursor

    async def create_comment(
        self,
        rich_text_str: str,
        *,
        page_id: str | None = None,
        discussion_id: str | None = None,
    ) -> None:
        if (page_id is None) == (discussion_id is None):
            raise ValueError("Specify exactly one parent: page_id OR discussion_id")

        # Convert plain text to rich text
        converter = MarkdownRichTextConverter()
        rich_text = await converter.to_rich_text(rich_text_str)

        if page_id:
            request = CommentCreateRequest.for_page(
                page_id=page_id,
                rich_text=rich_text,
            )
        else:
            request = CommentCreateRequest.for_discussion(
                discussion_id=discussion_id,
                rich_text=rich_text,
            )

        # Convert request to API format and make the call
        body = request.model_dump(exclude_unset=True, exclude_none=True)

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError("Failed to create CommentDto - check logs for HTTP error details.")

        return CommentDto.model_validate(resp)

    async def create_comment_on_page(
        self,
        page_id: str,
        text: str,
    ) -> None:
        return await self.create_comment(
            text,
            page_id=page_id,
        )

    async def reply_to_discussion(
        self,
        discussion_id: str,
        text: str,
    ) -> CommentDto:
        return await self.create_comment(
            text,
            discussion_id=discussion_id,
        )

    async def _list_comments(
        self,
        block_id: str,
        *,
        start_cursor: str | None = None,
        page_size: int = 100,
    ) -> CommentListResponse:
        request = CommentListRequest(
            block_id=block_id,
            start_cursor=start_cursor,
            page_size=page_size,
        )
        resp = await self.get("comments", params=request.to_params())
        if resp is None:
            raise RuntimeError("Failed to list comments.")
        return CommentListResponse.model_validate(resp)
