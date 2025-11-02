from typing import override

from notionary.rich_text.name_id_resolver.port import NameIdResolver
from notionary.workspace.query.service import WorkspaceQueryService


class DatabaseNameIdResolver(NameIdResolver):
    def __init__(self, search_service: WorkspaceQueryService | None = None) -> None:
        self.search_service = search_service or WorkspaceQueryService()

    @override
    async def resolve_name_to_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()
        database = await self.search_service.find_database(query=cleaned_name)
        return database.id if database else None

    @override
    async def resolve_id_to_name(self, database_id: str) -> str | None:
        if not database_id:
            return None

        try:
            from notionary import NotionDatabase

            database = await NotionDatabase.from_id(database_id)
            return database.title if database else None
        except Exception:
            return None
