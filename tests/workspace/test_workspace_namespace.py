from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.data_source.data_source import DataSource
from notionary.page.page import Page
from notionary.workspace.namespace import WorkspaceNamespace

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
DS_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

_PARTIAL_USER = {"object": "user", "id": "cccccccc-cccc-cccc-cccc-cccccccccccc"}
_WORKSPACE_PARENT = {"type": "workspace", "workspace": True}


def _page_raw() -> dict[str, Any]:
    return {
        "object": "page",
        "id": str(PAGE_ID),
        "created_time": "2025-01-01T00:00:00.000Z",
        "created_by": _PARTIAL_USER,
        "last_edited_time": "2025-06-01T00:00:00.000Z",
        "last_edited_by": _PARTIAL_USER,
        "cover": None,
        "icon": None,
        "parent": _WORKSPACE_PARENT,
        "in_trash": False,
        "url": "https://notion.so/test-page",
        "properties": {},
    }


def _data_source_raw() -> dict[str, Any]:
    return {
        "object": "data_source",
        "id": str(DS_ID),
        "created_time": "2025-01-01T00:00:00.000Z",
        "created_by": _PARTIAL_USER,
        "last_edited_time": "2025-06-01T00:00:00.000Z",
        "last_edited_by": _PARTIAL_USER,
        "cover": None,
        "icon": None,
        "parent": _WORKSPACE_PARENT,
        "database_parent": _WORKSPACE_PARENT,
        "in_trash": False,
        "url": "https://notion.so/test-ds",
        "title": [],
        "description": [],
        "is_inline": False,
        "is_locked": False,
        "data_sources": [],
        "properties": {},
    }


def _make_namespace() -> WorkspaceNamespace:
    http = AsyncMock()
    return WorkspaceNamespace(http)


def _fake_stream(*items: dict[str, Any]):
    async def _gen(**kwargs) -> AsyncGenerator[dict[str, Any]]:
        for item in items:
            yield item

    return _gen


class TestWorkspaceNamespaceSearch:
    @pytest.mark.asyncio
    async def test_search_returns_page_objects(self) -> None:
        ns = _make_namespace()
        ns._search_client.stream = _fake_stream(_page_raw())

        results = await ns.search()

        assert len(results) == 1
        assert isinstance(results[0], Page)

    @pytest.mark.asyncio
    async def test_search_returns_data_source_objects(self) -> None:
        ns = _make_namespace()
        ns._search_client.stream = _fake_stream(_data_source_raw())

        results = await ns.search()

        assert len(results) == 1
        assert isinstance(results[0], DataSource)

    @pytest.mark.asyncio
    async def test_search_aggregates_mixed_results(self) -> None:
        ns = _make_namespace()
        ns._search_client.stream = _fake_stream(_page_raw(), _data_source_raw())

        results = await ns.search()

        assert len(results) == 2
        types = {type(r) for r in results}
        assert Page in types
        assert DataSource in types

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_no_results(self) -> None:
        ns = _make_namespace()
        ns._search_client.stream = _fake_stream()

        results = await ns.search()

        assert results == []

    @pytest.mark.asyncio
    async def test_search_skips_unknown_object_types(self) -> None:
        ns = _make_namespace()
        unknown = {"object": "block", "id": str(PAGE_ID)}
        ns._search_client.stream = _fake_stream(unknown)

        results = await ns.search()

        assert results == []
