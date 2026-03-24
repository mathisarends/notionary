import asyncio

from notionary.http.client import HttpClient
from notionary.page.comments.client import CommentClient
from notionary.page.comments.factory import CommentFactory
from notionary.page.comments.models import Comment
from notionary.shared.rich_text.markdown_to_rich_text.factory import (
    create_markdown_to_rich_text_converter,
)


class PageComments:
    def __init__(self, page_id: str, http: HttpClient) -> None:
        self._page_id = page_id
        self._client = CommentClient(http)
        self._factory = CommentFactory()
        self._converter = create_markdown_to_rich_text_converter()

    async def list_all(self) -> list[Comment]:
        dtos = [dto async for dto in self._client.iter_comments(self._page_id)]
        return list(
            await asyncio.gather(*(self._factory.create_from_dto(dto) for dto in dtos))
        )

    async def create(self, text: str) -> Comment:
        rich_text = await self._converter.to_rich_text(text)
        dto = await self._client.create_comment_for_page(
            rich_text=rich_text, page_id=self._page_id
        )
        return await self._factory.create_from_dto(dto)

    async def reply_to(self, discussion_id: str, text: str) -> Comment:
        rich_text = await self._converter.to_rich_text(text)
        dto = await self._client.create_comment_for_discussion(
            rich_text=rich_text, discussion_id=discussion_id
        )
        return await self._factory.create_from_dto(dto)
