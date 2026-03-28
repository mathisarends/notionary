from uuid import UUID

from notionary.http import HttpClient
from notionary.page.schemas import PageDto


class PageHttpClient(HttpClient):
    def __init__(
        self,
        page_id: UUID,
        token: str | None = None,
    ):
        super().__init__(token=token)
        self._page_id = page_id

    async def get_page(self) -> PageDto:
        response = await self.get(f"pages/{self._page_id}")
        return PageDto.model_validate(response)
