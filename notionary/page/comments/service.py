import asyncio
import logging

from notionary.http.client import HttpClient
from notionary.page.comments.client import CommentClient
from notionary.page.comments.models import Comment
from notionary.page.comments.schemas import CommentDto
from notionary.shared.rich_text.markdown_to_rich_text.factory import (
    create_markdown_to_rich_text_converter,
)
from notionary.shared.rich_text.rich_text_to_markdown import RichTextToMarkdownConverter
from notionary.user import UserClient

logger = logging.getLogger(__name__)


class PageComments:
    def __init__(self, page_id: str, http: HttpClient) -> None:
        self._page_id = page_id
        self._client = CommentClient(http)
        self._user_client = UserClient(http)
        self._to_rich_text = create_markdown_to_rich_text_converter()
        self._to_markdown = RichTextToMarkdownConverter()

    async def list_all(self) -> list[Comment]:
        dtos = [dto async for dto in self._client.iter_comments(self._page_id)]
        return list(
            await asyncio.gather(*(self._comment_from_dto(dto) for dto in dtos))
        )

    async def create(self, text: str) -> Comment:
        dto = await self._client.create_comment_for_page(
            rich_text=await self._to_rich_text.to_rich_text(text),
            page_id=self._page_id,
        )
        return await self._comment_from_dto(dto)

    async def reply_to(self, discussion_id: str, text: str) -> Comment:
        dto = await self._client.create_comment_for_discussion(
            rich_text=await self._to_rich_text.to_rich_text(text),
            discussion_id=discussion_id,
        )
        return await self._comment_from_dto(dto)

    async def _comment_from_dto(self, dto: CommentDto) -> Comment:
        author, content = await asyncio.gather(
            self._resolve_author(dto.created_by.id),
            self._to_markdown.to_markdown(dto.rich_text),
        )
        return Comment(author_name=author, content=content)

    async def _resolve_author(self, user_id: str) -> str:
        try:
            dto = await self._user_client.get(user_id)
            return dto.name or "Unknown Author"
        except Exception:
            logger.warning(
                f"Failed to resolve user name for user_id: {user_id}", exc_info=True
            )
            return "Unknown Author"
