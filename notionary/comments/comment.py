import asyncio
from typing import Self

from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter
from notionary.comments.comment_models import CommentDto
from notionary.user.notion_person import NotionPersonFactory


class Comment:
    UNKNOWN_AUTHOR = "Unknown Author"

    def __init__(self, author_name: str, content: str, person_factory: NotionPersonFactory | None = None) -> None:
        self._author_name = author_name
        self._content = content

        self._person_factory = person_factory or NotionPersonFactory()

    @classmethod
    async def from_comment_dto(cls, dto: CommentDto) -> Self:
        author_name, content = await asyncio.gather(cls._resolve_user_name(dto), cls._reolve_content(dto))

        return cls(author_name=author_name, content=content)

    @classmethod
    async def _resolve_user_name(cls, dto: CommentDto) -> str:
        user_id = dto.created_by.id

        try:
            person = await NotionPersonFactory().from_user_id(user_id)
            if person and person.name:
                return person.name
        except Exception:
            return cls.UNKNOWN_AUTHOR

    @classmethod
    async def _reolve_content(cls, dto: CommentDto) -> str:
        rich_text_markdown_converter = RichTextToMarkdownConverter()

        return await rich_text_markdown_converter.to_markdown(dto.rich_text)
