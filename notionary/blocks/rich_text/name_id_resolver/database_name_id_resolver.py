from typing import override

from notionary.blocks.rich_text.name_id_resolver.name_id_resolver import NameIdResolver
from notionary.workspace.search.search_client import SearchClient


class DatabaseNameIdResolver(NameIdResolver):
    def __init__(self, search_client: SearchClient, search_limit: int = 100) -> None:
        self.search_client = search_client
        self.search_limit = search_limit

    @override
    async def resolve_id_to_name(self, name: str) -> str | None:
        database = await self.search_client.find_database(query=name, limit=self.search_limit)
        return database.id if database else None

    @override
    async def resolve_name_to_id(self, database_id: str) -> str | None:
        if not database_id:
            return None

        try:
            from notionary import NotionDatabase

            database = await NotionDatabase.from_id(database_id)
            return database.title if database else None
        except Exception:
            return None
