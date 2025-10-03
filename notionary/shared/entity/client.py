from typing import TypeVar, override

from notionary.http.client import NotionHttpClient
from notionary.shared.entity.entity_metadata_update_client import EntityMetadataUpdateClient
from notionary.shared.entity.schemas import EntityResponseDto, NotionEntityUpdateDto

ResponseType = TypeVar("ResponseType", bound=EntityResponseDto)


class GenericEntityMetadataUpdateClient(NotionHttpClient, EntityMetadataUpdateClient):
    def __init__(
        self,
        entity_id: str,
        path_segment: str,
        response_dto_class: type[ResponseType],
        timeout: int = 30,
    ) -> None:
        super().__init__(timeout)
        self._entity_id = entity_id
        self._path_segment = path_segment
        self._response_dto_class = response_dto_class

    @override
    async def patch_metadata(self, updated_data: NotionEntityUpdateDto) -> ResponseType:
        updated_data_dict = updated_data.model_dump(exclude_unset=True, exclude_none=True)
        url = f"{self._path_segment}/{self._entity_id}"

        response_dict = await self.patch(url, data=updated_data_dict)
        return self._response_dto_class.model_validate(response_dict)
