import asyncio

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.comments.models import Comment
from notionary.comments.schemas import CommentDto
from notionary.user.client import UserHttpClient
from notionary.user.person import PersonUser
from notionary.utils.mixins.logging import LoggingMixin


class CommentFactory(LoggingMixin):
    UNKNOWN_AUTHOR = "Unknown Author"

    def __init__(
        self,
        http_client: UserHttpClient | None = None,
        markdown_converter: RichTextToMarkdownConverter | None = None,
    ) -> None:
        self.http_client = http_client
        self.markdown_converter = markdown_converter or RichTextToMarkdownConverter()

    async def create_from_dto(self, dto: CommentDto) -> Comment:
        author_name, content = await asyncio.gather(self._resolve_user_name(dto), self._resolve_content(dto))

        return Comment(author_name=author_name, content=content)

    async def _resolve_user_name(self, dto: CommentDto) -> str:
        user_id = dto.created_by.id

        try:
            person = await PersonUser.from_id(user_id, self.http_client)
            if person and person.name:
                return person.name
        except Exception:
            self.logger.warning(f"Failed to resolve user name for user_id: {user_id}", exc_info=True)

        return self.UNKNOWN_AUTHOR

    async def _resolve_content(self, dto: CommentDto) -> str:
        return await self.markdown_converter.to_markdown(dto.rich_text)
