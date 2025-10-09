from collections.abc import AsyncGenerator

from notionary.blocks.rich_text.models import RichText
from notionary.comments.schemas import (
    CommentCreateRequest,
    CommentDto,
    CommentListRequest,
    CommentListResponse,
)
from notionary.http.client import NotionHttpClient
from notionary.utils.pagination import paginate_notion_api, paginate_notion_api_generator


class CommentClient(NotionHttpClient):
    def __init__(self) -> None:
        super().__init__()

    async def iter_comments(
        self,
        block_id: str,
        *,
        page_size: int = 100,
    ) -> AsyncGenerator[CommentDto]:
        """
        Iterates through all comments for a block, yielding each comment individually.
        Uses pagination to handle large result sets efficiently without loading everything into memory.
        """
        async for comment in paginate_notion_api_generator(
            self._list_comments_page, block_id=block_id, page_size=page_size
        ):
            yield comment

    async def get_all_comments(self, block_id: str, *, page_size: int = 100) -> list[CommentDto]:
        all_comments = await paginate_notion_api(self._list_comments_page, block_id=block_id, page_size=page_size)

        self.logger.debug("Retrieved %d total comments for block %s", len(all_comments), block_id)
        return all_comments

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
        resp = await self.get("comments", params=request.model_dump())
        return CommentListResponse.model_validate(resp)

    async def create_comment_for_page(
        self,
        rich_text: list[RichText],
        page_id: str,
    ) -> CommentDto:
        request = CommentCreateRequest.for_page(page_id=page_id, rich_text=rich_text)

        body = request.model_dump(exclude_unset=True, exclude_none=True)

        resp = await self.post("comments", data=body)
        return CommentDto.model_validate(resp)

    async def create_comment_for_discussion(
        self,
        rich_text: list[RichText],
        discussion_id: str,
    ) -> CommentDto:
        request = CommentCreateRequest.for_discussion(discussion_id=discussion_id, rich_text=rich_text)

        body = request.model_dump(exclude_unset=True, exclude_none=True)

        resp = await self.post("comments", data=body)
        return CommentDto.model_validate(resp)
