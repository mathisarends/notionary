from uuid import UUID

from pydantic import BaseModel

from notionary.http.client import HttpClient
from notionary.page.properties.schemas import PageProperty
from notionary.page.schemas import PageDto, PgePropertiesUpdateDto


class PagePropertyHttpClient:
    def __init__(
        self,
        page_id: UUID,
        http: HttpClient,
    ) -> None:
        self._page_id = page_id
        self._http = http

    async def patch_page(self, data: BaseModel) -> PageDto:
        result_dict = await self._http.patch(
            f"pages/{self._page_id}", data=data, exclude_unset=True
        )
        return PageDto.model_validate(result_dict)

    async def set_property(self, name: str, value: PageProperty) -> PageDto:
        return await self.patch_page(PgePropertiesUpdateDto(properties={name: value}))

    async def set_properties(self, values: dict[str, PageProperty]) -> PageDto:
        if not values:
            raise ValueError("At least one property must be provided.")
        return await self.patch_page(PgePropertiesUpdateDto(properties=values))
