from collections.abc import AsyncGenerator

from notionary.blocks.rich_text.rich_text_models import RichText
from notionary.comments.schemas import (
    CommentCreateRequest,
    CommentDto,
    CommentListRequest,
    CommentListResponse,
)
from notionary.http.http_client import NotionHttpClient


class CommentClient(NotionHttpClient):
    def __init__(self) -> None:
        super().__init__()

    async def iter_comments(
        self,
        block_id: str,
        *,
        page_size: int = 100,
    ) -> AsyncGenerator[CommentDto]:
        cursor: str | None = None

        while True:
            page = await self._list_comments_page(block_id, start_cursor=cursor, page_size=page_size)
            for item in page.results:
                yield item
            if not page.has_more:
                break
            cursor = page.next_cursor

    async def _list_comments_page(
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

    async def create_comment_for_page(
        self,
        rich_text: list[RichText],
        page_id: str,
    ) -> CommentDto:
        request = CommentCreateRequest.for_page(page_id=page_id, rich_text=rich_text)

        body = request.model_dump(exclude_unset=True, exclude_none=True)

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError("Failed to create CommentDto - check logs for HTTP error details.")

        return CommentDto.model_validate(resp)

    async def create_comment_for_discussion(
        self,
        rich_text: list[RichText],
        discussion_id: str,
    ) -> CommentDto:
        request = CommentCreateRequest.for_discussion(discussion_id=discussion_id, rich_text=rich_text)

        body = request.model_dump(exclude_unset=True, exclude_none=True)

        resp = await self.post("comments", data=body)
        if resp is None:
            raise RuntimeError("Failed to create CommentDto - check logs for HTTP error details.")

        return CommentDto.model_validate(resp)
