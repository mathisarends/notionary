import asyncio

from notionary import NotionPage
from notionary.data_source.data_source import NotionDataSource
from notionary.data_source.http.data_source_client import DataSourceClient
from notionary.database.database_models import NotionQueryDatabaseResponse
from notionary.http.http_client import NotionHttpClient
from notionary.page.search_filter_builder import SearchFilterBuilder
from notionary.user import NotionUser, NotionUserManager
from notionary.util import LoggingMixin


class NotionWorkspace(LoggingMixin):
    def __init__(self) -> None:
        self.notion_client = NotionHttpClient()
        self.user_manager = NotionUserManager()

    async def search_pages(self, query: str, sort_ascending: bool = True, limit: int = 100) -> list[NotionPage]:
        search_query = self._truncate_query_if_needed(query)

        search_filter = (
            SearchFilterBuilder()
            .with_query(search_query)
            .with_pages_only()
            .with_sort_direction("ascending" if sort_ascending else "descending")
            .with_page_size(limit)
        )

        result = await self.notion_client.post("search", search_filter.build())
        response = NotionQueryDatabaseResponse.model_validate(result)

        return await asyncio.gather(*(NotionPage.from_id(page.id) for page in response.results))

    async def search_data_sources(self, query: str, limit: int = 100) -> list[NotionDataSource]:
        search_query = self._truncate_query_if_needed(query)

        async with DataSourceClient() as data_source_client:
            response = await data_source_client.search_data_sources(query=search_query, limit=limit)
        return await asyncio.gather(*(NotionDataSource.from_id(data_source.id) for data_source in response.results))

    async def search_users(self, query: str, limit: int = 100) -> list[NotionUser]:
        search_query = self._truncate_query_if_needed(query)
        users = await self.user_manager.find_users_by_name(search_query)

        return users[:limit] if limit > 0 else users

    async def get_current_bot_user(self) -> NotionUser | None:
        return await self.user_manager.get_current_bot_user()

    async def get_user_by_id(self, user_id: str) -> NotionUser | None:
        return await self.user_manager.get_user_by_id(user_id)

    async def get_workspace_info(self) -> dict | None:
        return await self.user_manager.get_workspace_info()

    def _truncate_query_if_needed(self, query: str) -> str:
        MAX_WORDS = 4

        words = query.split()

        if len(words) > MAX_WORDS:
            truncated = " ".join(words[:MAX_WORDS])
            self.logger.debug(f"Query truncated from '{query}' to '{truncated}'")
            return truncated

        return query
