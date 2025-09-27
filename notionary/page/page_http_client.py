from notionary.http.http_client import NotionHttpClient
from notionary.page.page_models import NotionPageDto
from notionary.page.properties.page_property_models import PageProperty


class NotionPageHttpClient(NotionHttpClient):
    def __init__(
        self,
        page_id: str,
        properties: dict[str, PageProperty] | None = None,
    ):
        super().__init__()
        self._page_id = page_id
        self._page_properties = properties

    async def get_page(self) -> NotionPageDto:
        response = await self.get(f"pages/{self._page_id}")

        import json

        print(json.dumps(response, indent=2))

        page_dto = NotionPageDto.model_validate(response)
        return page_dto
