from typing import override

from notionary.database.models import NotionDatabaseDto

from notionary.http.http_client import NotionHttpClient
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient
from notionary.shared.entity.schemas import NotionEntityUpdateDto


class DatabaseMetadataUpdateClient(NotionHttpClient, EntityMetadataUpdateClient):
    def __init__(self, database_id: str, timeout: int = 30) -> None:
        super().__init__(timeout)
        self._database_id = database_id

    @override
    async def patch_metadata(self, updated_data: NotionEntityUpdateDto) -> NotionDatabaseDto:
        updated_data_dict = updated_data.model_dump(exclude_unset=True, exclude_none=True)

        response_dict = await self.patch(f"databases/{self._database_id}", data=updated_data_dict)
        return NotionDatabaseDto.model_validate(response_dict)
