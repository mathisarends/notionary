from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.data_source.client import DataSourceClient
from notionary.data_source.query.filters import (
    CheckboxCondition,
    CheckboxFilter,
    NumberCondition,
    NumberFilter,
)
from notionary.data_source.query.sorts import PropertySort, SortDirection
from notionary.page.page import Page

DS_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PAGE_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _page_response(page_id: UUID = PAGE_ID, title: str = "Test Page") -> dict:
    return {
        "object": "page",
        "id": str(page_id),
        "url": f"https://notion.so/{page_id}",
        "created_time": "2025-01-01T00:00:00.000Z",
        "created_by": {"id": str(USER_ID)},
        "last_edited_time": "2025-06-01T00:00:00.000Z",
        "last_edited_by": {"id": str(USER_ID)},
        "icon": None,
        "cover": None,
        "parent": {"type": "workspace", "workspace": True},
        "in_trash": False,
        "properties": {
            "Name": {
                "id": "title",
                "type": "title",
                "title": [
                    {"type": "text", "text": {"content": title}, "plain_text": title}
                ],
            }
        },
    }


def _make_client() -> tuple[DataSourceClient, AsyncMock]:
    http = AsyncMock()
    client = DataSourceClient(http=http, data_source_id=DS_ID)
    return client, http


class TestDataSourceClientQuery:
    @pytest.mark.asyncio
    async def test_query_returns_pages(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[_page_response()])

        pages = await client.query()

        assert len(pages) == 1
        assert isinstance(pages[0], Page)
        assert pages[0].id == PAGE_ID

    @pytest.mark.asyncio
    async def test_query_passes_filter_to_paginate(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[])

        f = CheckboxFilter(property="Done", checkbox=CheckboxCondition(equals=True))
        await client.query(filter=f)

        http.paginate.assert_called_once()
        kwargs = http.paginate.call_args
        assert kwargs.kwargs["filter"] == {
            "property": "Done",
            "checkbox": {"equals": True},
        }

    @pytest.mark.asyncio
    async def test_query_passes_sorts_to_paginate(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[])

        sorts = [PropertySort(property="Name", direction=SortDirection.DESCENDING)]
        await client.query(sorts=sorts)

        kwargs = http.paginate.call_args
        assert kwargs.kwargs["sorts"] == [
            {"property": "Name", "direction": "descending"}
        ]

    @pytest.mark.asyncio
    async def test_query_passes_limit(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[])

        await client.query(limit=10)

        http.paginate.assert_called_once()
        kwargs = http.paginate.call_args.kwargs
        assert kwargs["total_results_limit"] == 10

    @pytest.mark.asyncio
    async def test_query_passes_page_size(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[])

        await client.query(page_size=25)

        kwargs = http.paginate.call_args
        assert kwargs.kwargs["page_size"] == 25

    @pytest.mark.asyncio
    async def test_query_passes_in_trash(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[])

        await client.query(in_trash=True)

        kwargs = http.paginate.call_args
        assert kwargs.kwargs["in_trash"] is True

    @pytest.mark.asyncio
    async def test_query_uses_correct_endpoint(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[])

        await client.query()

        args = http.paginate.call_args
        assert args.args[0] == f"data_sources/{DS_ID}/query"

    @pytest.mark.asyncio
    async def test_query_multiple_pages_returned(self) -> None:
        client, http = _make_client()
        p1 = _page_response(PAGE_ID, "Page 1")
        p2_id = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
        p2 = _page_response(p2_id, "Page 2")
        http.paginate = AsyncMock(return_value=[p1, p2])

        pages = await client.query()

        assert len(pages) == 2
        assert pages[0].title == "Page 1"
        assert pages[1].title == "Page 2"

    @pytest.mark.asyncio
    async def test_query_empty_result(self) -> None:
        client, http = _make_client()
        http.paginate = AsyncMock(return_value=[])

        pages = await client.query()

        assert pages == []


class TestDataSourceClientIterQuery:
    @pytest.mark.asyncio
    async def test_iter_query_yields_pages(self) -> None:
        client, http = _make_client()

        async def fake_stream(*args, **kwargs):
            yield _page_response()

        http.paginate_stream = fake_stream

        pages = [p async for p in client.iter_query()]

        assert len(pages) == 1
        assert isinstance(pages[0], Page)
        assert pages[0].id == PAGE_ID

    @pytest.mark.asyncio
    async def test_iter_query_passes_filter(self) -> None:
        client, http = _make_client()
        captured_kwargs: dict = {}

        async def fake_stream(*args, **kwargs):
            captured_kwargs.update(kwargs)
            return
            yield  # make it a generator

        http.paginate_stream = fake_stream

        f = NumberFilter(property="Price", number=NumberCondition(greater_than=10))
        _ = [p async for p in client.iter_query(filter=f)]

        assert captured_kwargs["filter"] == {
            "property": "Price",
            "number": {"greater_than": 10},
        }

    @pytest.mark.asyncio
    async def test_iter_query_yields_multiple_pages(self) -> None:
        client, http = _make_client()
        p2_id = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")

        async def fake_stream(*args, **kwargs):
            yield _page_response(PAGE_ID, "First")
            yield _page_response(p2_id, "Second")

        http.paginate_stream = fake_stream

        pages = [p async for p in client.iter_query()]

        assert len(pages) == 2
        assert pages[0].title == "First"
        assert pages[1].title == "Second"

    @pytest.mark.asyncio
    async def test_iter_query_empty_stream(self) -> None:
        client, http = _make_client()

        async def fake_stream(*args, **kwargs):
            return
            yield

        http.paginate_stream = fake_stream

        pages = [p async for p in client.iter_query()]

        assert pages == []
