from __future__ import annotations

from typing import TYPE_CHECKING, cast

from notionary.shared.entity.schemas import EntityResponseDto
from notionary.shared.models.parent_models import DataSourceParent, ParentType

if TYPE_CHECKING:
    from notionary.data_source.service import NotionDataSource


async def extract_parent_data_source(response: EntityResponseDto) -> NotionDataSource | None:
    from notionary.data_source.service import NotionDataSource

    data_source_id = _extract_parent_data_source_id(response)
    if not data_source_id:
        return None

    return await NotionDataSource.from_id(data_source_id)


def _extract_parent_data_source_id(response: EntityResponseDto) -> str | None:
    if response.parent.type != ParentType.DATA_SOURCE_ID:
        return None
    data_source_parent = cast(DataSourceParent, response.parent)
    return data_source_parent.data_source_id if data_source_parent else None
