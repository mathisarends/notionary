from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.data_source.data_source import DataSource
from notionary.data_source.query.filters import (
    CheckboxCondition,
    CheckboxFilter,
    CompoundFilter,
    NumberCondition,
    NumberFilter,
    RichTextFilter,
    TextCondition,
)
from notionary.data_source.query.sorts import PropertySort, SortDirection
from notionary.page.page import Page
from notionary.user.schemas import PartialUserDto

DS_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PAGE_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _make_data_source() -> DataSource:
    http = AsyncMock()
    return DataSource(
        id=DS_ID,
        url="https://notion.so/test-ds",
        title="Test DS",
        description=None,
        icon=None,
        cover=None,
        in_trash=False,
        properties={},
        http=http,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


def _fake_page(page_id: UUID = PAGE_ID, title: str = "Page") -> Page:
    http = AsyncMock()
    return Page(
        id=page_id,
        url=f"https://notion.so/{page_id}",
        title=title,
        icon=None,
        cover=None,
        in_trash=False,
        properties={},
        http=http,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


class TestDataSourceQuery:
    @pytest.mark.asyncio
    async def test_query_delegates_to_client(self) -> None:
        ds = _make_data_source()
        expected = [_fake_page()]
        ds._client.query = AsyncMock(return_value=expected)

        result = await ds.query()

        ds._client.query.assert_called_once_with(
            filter=None,
            sorts=None,
            page_size=None,
            filter_properties=None,
            in_trash=None,
            limit=None,
        )
        assert result == expected

    @pytest.mark.asyncio
    async def test_query_passes_all_kwargs(self) -> None:
        ds = _make_data_source()
        ds._client.query = AsyncMock(return_value=[])

        f = CheckboxFilter(property="Done", checkbox=CheckboxCondition(equals=True))
        sorts = [PropertySort(property="Name", direction=SortDirection.DESCENDING)]

        await ds.query(
            filter=f,
            sorts=sorts,
            page_size=50,
            filter_properties=["Name"],
            in_trash=True,
            limit=10,
        )

        ds._client.query.assert_called_once_with(
            filter=f,
            sorts=sorts,
            page_size=50,
            filter_properties=["Name"],
            in_trash=True,
            limit=10,
        )

    @pytest.mark.asyncio
    async def test_query_with_compound_filter(self) -> None:
        ds = _make_data_source()
        ds._client.query = AsyncMock(return_value=[_fake_page()])

        f = CompoundFilter(
            and_=[
                CheckboxFilter(
                    property="Done", checkbox=CheckboxCondition(equals=True)
                ),
                RichTextFilter(
                    property="Name", rich_text=TextCondition(contains="test")
                ),
            ]
        )

        result = await ds.query(filter=f)

        assert len(result) == 1
        ds._client.query.assert_called_once()


class TestDataSourceIterQuery:
    @pytest.mark.asyncio
    async def test_iter_query_delegates_to_client(self) -> None:
        ds = _make_data_source()
        expected_page = _fake_page()

        async def fake_iter(**kwargs):
            yield expected_page

        ds._client.iter_query = fake_iter

        pages = [p async for p in ds.iter_query()]

        assert len(pages) == 1
        assert pages[0] == expected_page

    @pytest.mark.asyncio
    async def test_iter_query_passes_kwargs(self) -> None:
        ds = _make_data_source()
        captured_kwargs: dict = {}

        async def fake_iter(**kwargs):
            captured_kwargs.update(kwargs)
            return
            yield

        ds._client.iter_query = fake_iter

        f = NumberFilter(property="Price", number=NumberCondition(greater_than=100))
        _ = [p async for p in ds.iter_query(filter=f, limit=5)]

        assert captured_kwargs["filter"] is f
        assert captured_kwargs["limit"] == 5

    @pytest.mark.asyncio
    async def test_iter_query_yields_multiple(self) -> None:
        ds = _make_data_source()
        p1 = _fake_page(PAGE_ID, "First")
        p2 = _fake_page(UUID("dddddddd-dddd-dddd-dddd-dddddddddddd"), "Second")

        async def fake_iter(**kwargs):
            yield p1
            yield p2

        ds._client.iter_query = fake_iter

        pages = [p async for p in ds.iter_query()]

        assert len(pages) == 2
        assert pages[0].title == "First"
        assert pages[1].title == "Second"
