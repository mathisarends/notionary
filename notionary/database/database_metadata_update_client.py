from typing import override

from notionary.database.schemas import DatabaseDto
from notionary.http.client import HttpClient
from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.schemas import NotionEntityUpdateDto


class DatabaseMetadataUpdateClient(EntityMetadataUpdateClient):
    def __init__(self, database_id: str, http: HttpClient) -> None:
        self._database_id = database_id
        self._http = http

    @override
    async def patch_metadata(
        self, database_id: str, updated_data: NotionEntityUpdateDto
    ) -> DatabaseDto:
        updated_data_dict = updated_data.model_dump(
            exclude_unset=True, exclude_none=True
        )

        response_dict = await self._http.patch(
            f"databases/{database_id}", data=updated_data_dict
        )
        return DatabaseDto.model_validate(response_dict)
