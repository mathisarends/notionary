import asyncio

from notionary.blocks.rich_text.markdown_rich_text_converter import (
    MarkdownRichTextConverter,
)
from notionary.comments.client import CommentClient
from notionary.comments.factory import CommentFactory
from notionary.comments.models import Comment


class CommentService:
    def __init__(
        self,
        client: CommentClient | None = None,
        factory: CommentFactory | None = None,
        markdown_rich_text_converter: MarkdownRichTextConverter | None = None,
    ) -> None:
        self.client = client or CommentClient()
        self.factory = factory or CommentFactory()
        self._converter = markdown_rich_text_converter or MarkdownRichTextConverter()

    async def list_all_comments_for_page(self, page_id: str) -> list[Comment]:
        comment_dtos = [dto async for dto in self.client.iter_comments(page_id)]

        comments = await asyncio.gather(
            *(self.factory.create_from_dto(dto) for dto in comment_dtos)
        )
        return comments

    async def create_comment_on_page(self, page_id: str, text: str) -> Comment:
        rich_text = await self._converter.to_rich_text(text)
        comment_dto = await self.client.create_comment_for_page(
            rich_text=rich_text, page_id=page_id
        )
        return await self.factory.create_from_dto(comment_dto)

    async def reply_to_discussion_by_id(self, discussion_id: str, text: str) -> Comment:
        rich_text = await self._converter.to_rich_text(text)
        comment_dto = await self.client.create_comment_for_discussion(
            rich_text=rich_text, discussion_id=discussion_id
        )
        return await self.factory.create_from_dto(comment_dto)
