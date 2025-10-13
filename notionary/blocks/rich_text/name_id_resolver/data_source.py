from typing import override

from notionary.blocks.rich_text.name_id_resolver.port import NameIdResolver
from notionary.workspace.query.service import WorkspaceQueryService


# !!! in the notion api mentions that reference datasources are not provided yet (it's a limiation of the API as of now)
class DataSourceNameIdResolver(NameIdResolver):
    def __init__(self, workspace_query_service: WorkspaceQueryService | None = None) -> None:
        self._workspace_query_service = workspace_query_service or WorkspaceQueryService()

    @override
    async def resolve_name_to_id(self, name: str) -> str | None:
        if not name:
            return None

        cleaned_name = name.strip()
        data_source = await self._workspace_query_service.find_data_source(query=cleaned_name)
        return data_source.id if data_source else None

    @override
    async def resolve_id_to_name(self, data_source_id: str) -> str | None:
        if not data_source_id:
            return None

        try:
            from notionary import NotionDataSource

            data_source = await NotionDataSource.from_id(data_source_id)
            return data_source.title if data_source else None
        except Exception:
            return None
