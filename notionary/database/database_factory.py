from __future__ import annotations

from typing import TYPE_CHECKING, cast

from notionary.database.database_models import NotionDatabaseDto
from notionary.shared.entities.entity_factory import NotionEntityFactory
from notionary.shared.entities.entity_models import NotionEntityResponseDto
from notionary.util.fuzzy import find_best_match
from notionary.util.page_id_utils import format_uuid

if TYPE_CHECKING:
    from notionary import NotionDatabase


class NotionDatabaseFactory(NotionEntityFactory):
    async def load_from_id(self, database_id: str) -> NotionDatabase:
        formatted_id = format_uuid(database_id) or database_id
        response = await self._fetch_database_response(formatted_id)
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

    async def _extract_title(self, response: NotionEntityResponseDto) -> str:
        database_response: NotionDatabaseDto = cast(NotionDatabaseDto, response)
        rich_text_title = database_response.title
        return await self._extract_title_from_rich_text_objects(rich_text_title)

    async def _fetch_database_response(self, database_id: str) -> NotionEntityResponseDto:
        from notionary.database.database_http_client import NotionDatabseHttpClient

        async with NotionDatabseHttpClient(database_id=database_id) as client:
            return await client.get_database()

    async def _create_database_from_response(self, response: NotionEntityResponseDto) -> NotionDatabase:
        from notionary import NotionDatabase

        entity_kwargs = await self._create_common_entity_kwargs(response)
        return NotionDatabase(**entity_kwargs)


async def load_database_from_id(database_id: str) -> NotionDatabase:
    factory = NotionDatabaseFactory()
    return await factory.load_from_id(database_id)


async def load_database_from_title(database_title: str, min_similarity: float = 0.6) -> NotionDatabase:
    factory = NotionDatabaseFactory()
    return await factory.load_from_title(database_title, min_similarity)
