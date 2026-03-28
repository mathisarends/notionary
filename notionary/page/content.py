import logging
from uuid import UUID

from notionary.http import HttpClient
from notionary.page.content.schemas import (
    InsertContentRequest,
    PageMarkdownResponse,
    ReplaceContentRequest,
)

logger = logging.getLogger(__name__)


class PageContent:
    def __init__(self, page_id: UUID, http: HttpClient) -> None:
        self._page_id = page_id
        self._http = http

    async def get_markdown(self) -> str:
        response = await self._http.get(f"pages/{self._page_id}/markdown")
        return PageMarkdownResponse.model_validate(response).markdown

    async def append(self, content: str) -> None:
        if not content:
            logger.debug("No markdown content to append for page: %s", self._page_id)
            return
        request = InsertContentRequest.from_markdown(content)
        await self._http.patch(f"pages/{self._page_id}/markdown", data=request)

    async def replace(self, content: str) -> None:
        request = ReplaceContentRequest.from_markdown(content)
        await self._http.patch(f"pages/{self._page_id}/markdown", data=request)

    async def clear(self) -> None:
        await self.replace("")
