from __future__ import annotations

from typing import TYPE_CHECKING

from notionary.database.database_models import NotionDatabaseDto
from notionary.util.fuzzy import find_best_match

if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionDatabaseFactory:
    async def load_from_id(self, database_id: str) -> NotionDatabase:
        response = await self._fetch_database_response(database_id)
        import json

        print("Database Response:", json.dumps(response.model_dump(), indent=2))

        return await self._create_database_from_response(response)

    async def load_from_title(self, database_title: str, min_similarity: float = 0.6) -> NotionDatabase:
        from notionary.workspace import NotionWorkspace

        workspace = NotionWorkspace()
        search_results = await workspace.search_databases(database_title, limit=10)

        if not search_results:
            raise ValueError(f"No databases found for name: {database_title}")

        best_match = find_best_match(
            query=database_title,
            items=search_results,
            text_extractor=lambda database: database.title,
            min_similarity=min_similarity,
        )

        if not best_match:
            available_titles = [result.title for result in search_results[:5]]
            raise ValueError(
                f"No sufficiently similar database found for '{database_title}'. Available: {available_titles}"
            )

        return await self.load_from_id(best_match.item.id)

    async def _extract_title(self, response: NotionDatabaseDto) -> str:
        rich_text_title = response.title
        return await self._extract_title_from_rich_text_objects(rich_text_title)

    async def _fetch_database_response(self, database_id: str) -> NotionDatabaseDto:
        from notionary.database.database_http_client import NotionDatabseHttpClient

        async with NotionDatabseHttpClient(database_id=database_id) as client:
            return await client.get_database()

    async def _create_database_from_response(self, response: NotionDatabaseDto) -> NotionDatabase:
        from notionary import NotionDatabase

        entity_kwargs = await self._create_common_entity_kwargs(response)

        entity_kwargs["is_inline"] = response.is_inline
        entity_kwargs["description"] = await self._extract_description(response)

        return NotionDatabase(**entity_kwargs)

    async def _create_common_entity_kwargs(self, response: NotionDatabaseDto) -> dict:
        title = await self._extract_title(response)
        emoji_icon = self._extract_emoji_icon(response)
        external_icon_url = self._extract_external_icon_url(response)
        cover_image_url = self._extract_cover_image_url(response)

        return {
            "id": str(response.id),
            "title": title,
            "created_time": response.created_time,
            "last_edited_time": response.last_edited_time,
            "in_trash": response.in_trash,
            "emoji_icon": emoji_icon,
            "external_icon_url": external_icon_url,
            "cover_image_url": cover_image_url,
            "url": response.url,
            "public_url": response.public_url,
        }

    def _extract_emoji_icon(self, response: NotionDatabaseDto) -> str | None:
        from notionary.shared.models.icon_models import IconType

        if not response.icon or response.icon.type != IconType.EMOJI:
            return None
        return response.icon.emoji

    def _extract_external_icon_url(self, response: NotionDatabaseDto) -> str | None:
        from notionary.shared.models.icon_models import IconType

        if not response.icon or response.icon.type != IconType.EXTERNAL:
            return None
        return response.icon.external.url if response.icon.external else None

    def _extract_cover_image_url(self, response: NotionDatabaseDto) -> str | None:
        from notionary.shared.models.cover_models import CoverType

        if not response.cover or response.cover.type != CoverType.EXTERNAL:
            return None
        return response.cover.external.url if response.cover.external else None

    async def _extract_description(self, response: NotionDatabaseDto) -> str:
        from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter

        description_rich_text = response.description

        rich_text_markdown_converter = RichTextToMarkdownConverter()

        return await rich_text_markdown_converter.to_markdown(description_rich_text)

    async def _extract_title_from_rich_text_objects(self, rich_text_objects: list) -> str:
        from notionary.blocks.rich_text.rich_text_markdown_converter import RichTextToMarkdownConverter

        rich_text_markdown_converter = RichTextToMarkdownConverter()
        title = await rich_text_markdown_converter.to_markdown(rich_text_objects)
        return title


async def load_database_from_id(database_id: str) -> NotionDatabase:
    factory = NotionDatabaseFactory()
    return await factory.load_from_id(database_id)


async def load_database_from_title(database_title: str, min_similarity: float = 0.6) -> NotionDatabase:
    factory = NotionDatabaseFactory()
    return await factory.load_from_title(database_title, min_similarity)
