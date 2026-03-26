import logging

from pydantic import BaseModel

from notionary.http import HttpClient

logger = logging.getLogger(__name__)


class PageMarkdownResponse(BaseModel):
    object: str
    id: str
    markdown: str
    truncated: bool
    unknown_block_ids: list[str]


class PageContent:
    def __init__(self, page_id: str, http: HttpClient) -> None:
        self._page_id = page_id
        self._http = http

    async def get_markdown(self) -> str:
        response = await self._http.get(f"pages/{self._page_id}/markdown")
        dto = PageMarkdownResponse.model_validate(response)
        return dto.markdown

    async def append(self, content: str) -> None:
        if not content:
            logger.debug("No markdown content to append for page: %s", self._page_id)
            return
        await self._http.patch(
            f"pages/{self._page_id}/markdown",
            data={
                "type": "insert_content",
                "insert_content": {
                    "content": content,
                },
            },
        )

    async def replace(self, content: str) -> None:
        await self._http.patch(
            f"pages/{self._page_id}/markdown",
            data={
                "type": "replace_content",
                "replace_content": {
                    "new_str": content,
                },
            },
        )

    async def clear(self) -> None:
        await self.replace("")
