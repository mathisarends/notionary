from __future__ import annotations

from collections.abc import Callable

from notionary.blocks.block_http_client import NotionBlockHttpClient
from notionary.blocks.markdown.markdown_builder import MarkdownBuilder
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.blocks.syntax_prompt_builder import SyntaxPromptBuilder
from notionary.comments.models import Comment
from notionary.comments.service import CommentService
from notionary.file_upload.file_upload_http_client import FileUploadHttpClient
from notionary.page.factory import (
    load_page_from_id,
    load_page_from_title,
)
from notionary.page.page_content_deleting_service import PageContentDeletingService
from notionary.page.page_content_writer import PageContentWriter
from notionary.page.page_context import PageContextProvider, page_context
from notionary.page.page_http_client import NotionPageHttpClient
from notionary.page.page_metadata_update_client import PageMetadataUpdateClient
from notionary.page.properties.service import PagePropertyHandler
from notionary.page.reader.page_content_retriever import PageContentRetriever
from notionary.schemas import NotionContentSchema
from notionary.shared.entity.entity import Entity


class NotionPage(Entity):
    def __init__(
        self,
        id: str,
        title: str,
        created_time: str,
        last_edited_time: str,
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
            last_edited_time=last_edited_time,
            in_trash=in_trash,
            emoji_icon=emoji_icon,
            external_icon_url=external_icon_url,
            cover_image_url=cover_image_url,
        )
        self._title = title
        self._archived = archived
        self._url = url
        self._public_url = public_url

        self._page_client = NotionPageHttpClient(
            page_id=id,
        )
        self._block_client = NotionBlockHttpClient()
        self._comment_service = CommentService()

        self.block_element_registry = BlockRegistry()

        self._page_content_writer = PageContentWriter(
            page_id=self._id,
            block_registry=self.block_element_registry,
        )

        self._page_content_deleting_service = PageContentDeletingService(
            page_id=self._id,
            block_registry=self.block_element_registry,
        )

        self._page_content_retriever = PageContentRetriever(
            block_registry=self.block_element_registry,
        )

        self.page_context_provider = self._setup_page_context_provider()
        self.properties = page_property_handler

        self._metadata_update_client = PageMetadataUpdateClient(page_id=id)

    @classmethod
    async def from_id(cls, id: str) -> NotionPage:
        return await load_page_from_id(id)

    @classmethod
    async def from_title(cls, title: str, min_similarity: float = 0.6) -> NotionPage:
        return await load_page_from_title(title, min_similarity)

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
        async with page_context(self.page_context_provider):
            _ = await self._page_content_writer.append_markdown(content=content)

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

    def _setup_page_context_provider(self) -> PageContextProvider:
        return PageContextProvider(
            page_id=self._id,
            file_upload_client=FileUploadHttpClient(),
        )
