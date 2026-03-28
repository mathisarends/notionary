import asyncio
import logging
from uuid import UUID

from notionary.http.client import HttpClient
from notionary.page.comments.client import CommentClient
from notionary.page.comments.models import Comment
from notionary.page.comments.schemas import CommentDto
from notionary.rich_text import markdown_to_rich_text, rich_text_to_markdown
from notionary.user import UserClient

logger = logging.getLogger(__name__)


class PageComments:
    """Scoped access to comments on a single Notion page."""

    def __init__(self, page_id: UUID, http: HttpClient) -> None:
        self._page_id = page_id
        self._client = CommentClient(http)
        self._user_client = UserClient(http)

    async def list_all(self) -> list[Comment]:
        """Return all comments on this page.

        Returns:
            A list of :class:`~notionary.page.comments.models.Comment` objects
            with resolved author names.
        """
        dtos = [dto async for dto in self._client.iter_comments(self._page_id)]
        return list(
            await asyncio.gather(*(self._comment_from_dto(dto) for dto in dtos))
        )

    async def create(self, text: str) -> Comment:
        """Add a top-level comment to the page.

        Args:
            text: Markdown text of the comment.

        Returns:
            The created :class:`~notionary.page.comments.models.Comment`.
        """
        dto = await self._client.create_comment_for_page(
            rich_text=markdown_to_rich_text(text),
            page_id=self._page_id,
        )
        return await self._comment_from_dto(dto)

    async def _comment_from_dto(self, dto: CommentDto) -> Comment:
        content = rich_text_to_markdown(dto.rich_text)
        author = await self._resolve_author(dto.created_by.id)
        return Comment(author_name=author, content=content)

    async def _resolve_author(self, user_id: UUID) -> str:
        try:
            dto = await self._user_client.get(user_id)
            return dto.name or "Unknown Author"
        except Exception:
            logger.warning(
                f"Failed to resolve user name for user_id: {user_id}", exc_info=True
            )
            return "Unknown Author"
