import logging
from collections.abc import AsyncGenerator
from uuid import UUID

from notionary.http.client import HttpClient
from notionary.page.comments.schemas import CommentCreateRequest, CommentDto
from notionary.rich_text.schemas import RichText

logger = logging.getLogger(__name__)


class CommentClient:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def iter_comments(
        self,
        block_id: UUID,
        total_results_limit: int | None = None,
    ) -> AsyncGenerator[CommentDto]:
        async for item in self._http.paginate_stream(
            "comments",
            total_results_limit=total_results_limit,
            method="GET",
            block_id=block_id,
        ):
            yield CommentDto.model_validate(item)

    async def get_all_comments(
        self,
        block_id: UUID,
        *,
        total_results_limit: int | None = None,
    ) -> list[CommentDto]:
        items = await self._http.paginate(
            "comments",
            total_results_limit=total_results_limit,
            method="GET",
            block_id=block_id,
        )
        comments = [CommentDto.model_validate(item) for item in items]
        logger.debug(
            "Retrieved %d total comments for block %s", len(comments), block_id
        )
        return comments

    async def create_comment_for_page(
        self,
        rich_text: list[RichText],
        page_id: UUID,
    ) -> CommentDto:
        body = CommentCreateRequest.for_page(
            page_id=page_id, rich_text=rich_text
        ).model_dump(exclude_unset=True, exclude_none=True)
        return CommentDto.model_validate(await self._http.post("comments", data=body))

    async def create_comment_for_discussion(
        self,
        rich_text: list[RichText],
        discussion_id: UUID,
    ) -> CommentDto:
        body = CommentCreateRequest.for_discussion(
            discussion_id=discussion_id, rich_text=rich_text
        ).model_dump(exclude_unset=True, exclude_none=True)
        return CommentDto.model_validate(await self._http.post("comments", data=body))
