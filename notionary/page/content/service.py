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
    """Read and write page content as markdown."""

    def __init__(self, page_id: UUID, http: HttpClient) -> None:
        self._page_id = page_id
        self._http = http

    async def get_markdown(self) -> str:
        """Return the full page content as a markdown string."""
        response = await self._http.get(f"pages/{self._page_id}/markdown")
        return PageMarkdownResponse.model_validate(response).markdown

    async def append(self, content: str) -> None:
        """Append markdown content to the end of the page.

        Args:
            content: Markdown string to append. Empty strings are ignored.
        """
        if not content:
            logger.debug("No markdown content to append for page: %s", self._page_id)
            return
        request = InsertContentRequest.from_markdown(content)
        await self._http.patch(
            f"pages/{self._page_id}/markdown", data=request.model_dump()
        )

    async def replace(self, content: str) -> None:
        """Replace the entire page body with new markdown content.

        Args:
            content: Markdown string that replaces existing content.
        """
        request = ReplaceContentRequest.from_markdown(content)
        await self._http.patch(
            f"pages/{self._page_id}/markdown", data=request.model_dump()
        )

    async def clear(self) -> None:
        """Remove all content from the page."""
        await self.replace("")
