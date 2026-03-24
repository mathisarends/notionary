from typing import override

from notionary.http.client import NotionHttpClient
from notionary.page.schemas import PageDto
from notionary.shared.entity.entity_metadata_update_client import (
    EntityMetadataUpdateClient,
)
from notionary.shared.entity.schemas import NotionEntityUpdateDto


class PageMetadataUpdateClient(NotionHttpClient, EntityMetadataUpdateClient):
    def __init__(
        self, page_id: str, token: str | None = None, timeout: int = 30
    ) -> None:
        super().__init__(token=token, timeout=timeout)
        self._page_id = page_id

    @override
    async def patch_metadata(self, updated_data: NotionEntityUpdateDto) -> PageDto:
        updated_data_dict = updated_data.model_dump(
            exclude_unset=True, exclude_none=True
        )

        response_dict = await self.patch(
            f"pages/{self._page_id}", data=updated_data_dict
        )
        return PageDto.model_validate(response_dict)
