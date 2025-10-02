from notionary.http.http_client import NotionHttpClient
from notionary.page.page_models import NotionPageDto


class NotionPageHttpClient(NotionHttpClient):
    def __init__(
        self,
        page_id: str,
    ):
        super().__init__()
        self._page_id = page_id

    async def get_page(self) -> NotionPageDto:
        response = await self.get(f"pages/{self._page_id}")
        return NotionPageDto.model_validate(response)
