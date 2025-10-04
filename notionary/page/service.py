import asyncio
from collections.abc import Callable
from typing import Self

from notionary.blocks.client import NotionBlockHttpClient
from notionary.blocks.mappings.rich_text.rich_text_markdown_converter import convert_rich_text_to_markdown
from notionary.blocks.markdown.builder import MarkdownBuilder
from notionary.blocks.registry.service import BlockRegistry
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder
from notionary.comments.models import Comment
from notionary.comments.service import CommentService
from notionary.page.content.page_content_deleting_service import PageContentDeletingService
from notionary.page.content.reader.service import NotionToMarkdownConverter
from notionary.page.content.writer.service import PageContentWriter
from notionary.page.page_http_client import NotionPageHttpClient
from notionary.page.page_metadata_update_client import PageMetadataUpdateClient
from notionary.page.properties.factory import PagePropertyHandlerFactory
from notionary.page.properties.models import PageTitleProperty
from notionary.page.properties.service import PagePropertyHandler
from notionary.page.schemas import NotionPageDto
from notionary.schemas import NotionContentSchema
from notionary.search.service import SearchService
from notionary.shared.entity.dto_parsers import (
    extract_cover_image_url_from_dto,
    extract_emoji_icon_from_dto,
    extract_external_icon_url_from_dto,
)
from notionary.shared.entity.service import Entity
from notionary.user.schemas import PartialUserDto


class NotionPage(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        created_by: PartialUserDto,
        last_edited_time: str,
        last_edited_by: PartialUserDto,
        url: str,
        archived: bool,
        in_trash: bool,
        page_property_handler: PagePropertyHandler,
        public_url: str | None = None,
        emoji_icon: str | None = None,
        external_icon_url: str | None = None,
        cover_image_url: str | None = None,
    ) -> None:
        super().__init__(
            id=id,
            created_time=created_time,
            created_by=created_by,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._title = title
        self._archived = archived
        self._url = url
        self._public_url = public_url

        self._block_client = NotionBlockHttpClient()
        self._comment_service = CommentService()

        self.block_element_registry = BlockRegistry()

        self._page_content_writer = PageContentWriter(
            page_id=self._id, block_registry=self.block_element_registry, block_client=self._block_client
        )

        self._page_content_deleting_service = PageContentDeletingService(
            page_id=self._id, block_registry=self.block_element_registry, block_client=self._block_client
        )

        self._page_content_retriever = NotionToMarkdownConverter(
            block_registry=self.block_element_registry,
        )

        self.properties = page_property_handler

        self._metadata_update_client = PageMetadataUpdateClient(page_id=id)

    @classmethod
    async def from_id(
        cls,
        page_id: str,
        page_property_handler_factory: PagePropertyHandlerFactory | None = None,
    ) -> Self:
        factory = page_property_handler_factory or PagePropertyHandlerFactory()
        response = await cls._fetch_page_dto(page_id)
        return await cls._create_from_dto(response, factory)

    @classmethod
    async def from_title(
        cls,
        page_title: str,
        min_similarity: float = 0.6,
        search_service: SearchService | None = None,
    ) -> Self:
        service = search_service or SearchService()
        return await service.find_page(page_title, min_similarity=min_similarity)

    @classmethod
    async def _fetch_page_dto(cls, page_id: str) -> NotionPageDto:
        async with NotionPageHttpClient(page_id=page_id) as client:
            return await client.get_page()

    @classmethod
    async def _create_from_dto(
        cls,
        response: NotionPageDto,
        page_property_handler_factory: PagePropertyHandlerFactory,
    ) -> Self:
        title, page_property_handler = await asyncio.gather(
            cls._extract_title_from_dto(response),
            page_property_handler_factory.create_from_page_response(response),
        )

        return cls(
            id=response.id,
            title=title,
            created_time=response.created_time,
            created_by=response.created_by,
            last_edited_time=response.last_edited_time,
            last_edited_by=response.last_edited_by,
            archived=response.archived,
            in_trash=response.in_trash,
            url=response.url,
            page_property_handler=page_property_handler,
            public_url=response.public_url,
            emoji_icon=extract_emoji_icon_from_dto(response),
            external_icon_url=extract_external_icon_url_from_dto(response),
            cover_image_url=extract_cover_image_url_from_dto(response),
        )

    @staticmethod
    async def _extract_title_from_dto(response: NotionPageDto) -> str:
        title_property = next(
            (prop for prop in response.properties.values() if isinstance(prop, PageTitleProperty)),
            None,
        )
        rich_text_title = title_property.title if title_property else []
        return await convert_rich_text_to_markdown(rich_text_title)

    @property
    def _entity_metadata_update_client(self) -> PageMetadataUpdateClient:
        return self._metadata_update_client

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    def get_prompt_information(self) -> str:
        markdown_syntax_builder = SyntaxPromptBuilder()
        return markdown_syntax_builder.build_concise_reference()

    async def get_comments(self) -> list[Comment]:
        return await self._comment_service.list_all_comments_for_page(page_id=self._id)

    async def post_top_level_comment(self, comment: str) -> None:
        await self._comment_service.create_comment_on_page(page_id=self._id, text=comment)

    async def post_reply_to_discussion(self, discussion_id: str, comment: str) -> None:
        await self._comment_service.reply_to_discussion_by_id(discussion_id=discussion_id, text=comment)

    async def set_title(self, title: str) -> None:
        await self.properties.set_title_property(title)
        self._title = title

    async def append_markdown(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder] | NotionContentSchema),
    ) -> None:
        await self._page_content_writer.append_markdown(content=content)

    async def replace_content(
        self,
        content: (str | Callable[[MarkdownBuilder], MarkdownBuilder] | NotionContentSchema),
    ) -> None:
        await self._page_content_deleting_service.clear_page_content()
        await self._page_content_writer.append_markdown(content=content)

    async def clear_page_content(self) -> None:
        await self._page_content_deleting_service.clear_page_content()

    async def get_markdown_content(self) -> str:
        blocks = await self._block_client.get_blocks_by_page_id_recursively(page_id=self._id)
        return await self._page_content_retriever.convert_to_markdown(blocks=blocks)
