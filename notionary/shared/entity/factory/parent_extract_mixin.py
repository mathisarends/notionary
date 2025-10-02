from __future__ import annotations

from typing import TYPE_CHECKING, cast

from notionary.shared.entity.entity_models import EntityDto
from notionary.shared.models.parent_models import (
    DatabaseParent,
    DataSourceParent,
    ParentType,
)

if TYPE_CHECKING:
    from notionary.data_source.service import NotionDataSource
    from notionary.database.service import NotionDatabase


class ParentExtractMixin:
    async def _extract_parent_database(self, response: EntityDto) -> NotionDatabase | None:
        from notionary.database.service import NotionDatabase

        database_id = self._extract_parent_database_id(response)
        if not database_id:
            return None

        return await NotionDatabase.from_id(database_id)

    def _extract_parent_database_id(self, response: EntityDto) -> str | None:
        if response.parent.type == ParentType.DATA_SOURCE_ID:
            data_source_parent = cast(DataSourceParent, response.parent)
            return data_source_parent.database_id if data_source_parent else None

        if response.parent.type == ParentType.DATABASE_ID:
            database_parent = cast(DatabaseParent, response.parent)
            return database_parent.database_id if database_parent else None

    async def _extract_parent_data_source(self, response: EntityDto) -> NotionDataSource | None:
        from notionary.data_source.service import NotionDataSource

        data_source_id = self._extract_parent_data_source_id(response)
        if not data_source_id:
            return None

        return await NotionDataSource.from_id(data_source_id)

    def _extract_parent_data_source_id(self, response: EntityDto) -> str | None:
        if response.parent.type != ParentType.DATA_SOURCE_ID:
            return None
        data_source_parent = cast(DataSourceParent, response.parent)
        return data_source_parent.data_source_id if data_source_parent else None
