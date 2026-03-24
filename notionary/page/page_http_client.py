from notionary.http.client import NotionHttpClient
from notionary.page.schemas import PageDto


class PageHttpClient(NotionHttpClient):
    def __init__(
        self,
        page_id: str,
        token: str | None = None,
    ):
        super().__init__(token=token)
        self._page_id = page_id

    async def get_page(self) -> PageDto:
        response = await self.get(f"pages/{self._page_id}")
        return PageDto.model_validate(response)
