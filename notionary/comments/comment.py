import asyncio
from typing import Self

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.comments.comment_models import CommentDto
from notionary.user.notion_user import NotionUser


# TODO: Make models more consistent and the api (and make it possible to respond to a comment like this via this object for example)
# allow for comments not only on pages but on blocks as well.
class Comment:
    def __init__(self, author_name: str, content: str) -> None:
        self.author_name = author_name
        self.content = content

    @classmethod
    async def from_comment_dto(cls, dto: CommentDto) -> Self:
        author_name, content = await asyncio.gather(cls._resolve_user_name(dto), cls._reolve_content(dto))

        return cls(author_name=author_name, content=content)

    @classmethod
    async def _resolve_user_name(cls, dto: CommentDto) -> str:
        user_id = dto.created_by.id

        user = await NotionUser.from_user_id(user_id)
        return user.name if user else "Unknown"

    @classmethod
    async def _reolve_content(cls, dto: CommentDto) -> str:
        rich_text_markdown_converter = RichTextToMarkdownConverter()

        return await rich_text_markdown_converter.to_markdown(dto.rich_text)
