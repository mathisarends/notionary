from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest

from notionary.shared.search.client import SearchClient


def _fake_paginate_stream(*items: dict[str, Any]):
    async def _gen(**kwargs) -> AsyncGenerator[dict[str, Any]]:
        for item in items:
            yield item

    return _gen


def _make_client() -> tuple[SearchClient, AsyncMock]:
    http = AsyncMock()
    client = SearchClient(http)
    return client, http


class TestSearchClientStream:
    @pytest.mark.asyncio
    async def test_stream_yields_all_items(self) -> None:
        client, http = _make_client()
        http.paginate_stream = _fake_paginate_stream({"id": "1"}, {"id": "2"})

        results = [item async for item in client.stream()]

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_stream_yields_empty_when_no_results(self) -> None:
        client, http = _make_client()
        http.paginate_stream = _fake_paginate_stream()

        results = [item async for item in client.stream()]

        assert results == []

    @pytest.mark.asyncio
    async def test_stream_passes_query_to_paginate(self) -> None:
        client, http = _make_client()
        calls = []

        async def _capture(**kwargs) -> AsyncGenerator[dict[str, Any]]:
            calls.append(kwargs)
            return
            yield  # make it a generator

        http.paginate_stream = _capture

        async for _ in client.stream(query="my query"):
            pass

        assert calls[0]["query"] == "my query"

    @pytest.mark.asyncio
    async def test_stream_passes_total_results_limit(self) -> None:
        client, http = _make_client()
        calls = []

        async def _capture(**kwargs) -> AsyncGenerator[dict[str, Any]]:
            calls.append(kwargs)
            return
            yield

        http.paginate_stream = _capture

        async for _ in client.stream(total_results_limit=10):
            pass

        assert calls[0]["total_results_limit"] == 10
