from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.content.service import PageContent

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def _make_service() -> tuple[PageContent, AsyncMock]:
    http = AsyncMock()
    service = PageContent(page_id=PAGE_ID, http=http)
    return service, http


class TestPageContentGetMarkdown:
    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self) -> None:
        service, http = _make_service()
        http.get.return_value = {
            "object": "page",
            "id": str(PAGE_ID),
            "markdown": "# Hello",
            "truncated": False,
            "unknown_block_ids": [],
        }

        await service.get_markdown()

        http.get.assert_called_once_with(f"pages/{PAGE_ID}/markdown")

    @pytest.mark.asyncio
    async def test_get_returns_markdown_string(self) -> None:
        service, http = _make_service()
        http.get.return_value = {
            "object": "page",
            "id": str(PAGE_ID),
            "markdown": "# Hello World",
            "truncated": False,
            "unknown_block_ids": [],
        }

        result = await service.get_markdown()

        assert result == "# Hello World"


class TestPageContentAppend:
    @pytest.mark.asyncio
    async def test_append_calls_patch_with_content(self) -> None:
        service, http = _make_service()

        await service.append("## Section")

        http.patch.assert_called_once()
        args, _kwargs = http.patch.call_args
        assert args[0] == f"pages/{PAGE_ID}/markdown"

    @pytest.mark.asyncio
    async def test_append_skips_empty_content(self) -> None:
        service, http = _make_service()

        await service.append("")

        http.patch.assert_not_called()

    @pytest.mark.asyncio
    async def test_append_skips_none_like_falsy_content(self) -> None:
        service, http = _make_service()

        await service.append("   "[:-3])  # empty string

        http.patch.assert_not_called()


class TestPageContentReplace:
    @pytest.mark.asyncio
    async def test_replace_calls_patch(self) -> None:
        service, http = _make_service()

        await service.replace("New content")

        http.patch.assert_called_once()
        args, _ = http.patch.call_args
        assert args[0] == f"pages/{PAGE_ID}/markdown"


class TestPageContentClear:
    @pytest.mark.asyncio
    async def test_clear_calls_replace_with_empty_string(self) -> None:
        service, http = _make_service()

        await service.clear()

        http.patch.assert_called_once()
        _, kwargs = http.patch.call_args
        request = kwargs["data"]
        assert request.replace_content.new_str == ""
