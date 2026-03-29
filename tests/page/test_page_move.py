from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary import Page
from notionary.page.schemas import (
    DataSourceParent,
    MovePageRequest,
    PageParent,
)

PAGE_ID = UUID("11111111-1111-1111-1111-111111111111")
PARENT_PAGE_ID = UUID("22222222-2222-2222-2222-222222222222")
DATA_SOURCE_ID = UUID("33333333-3333-3333-3333-333333333333")


class TestMovePageRequestSchema:
    def test_page_parent_serialization(self) -> None:
        request = MovePageRequest(parent=PageParent(page_id=PARENT_PAGE_ID))
        data = request.model_dump(exclude_none=True, mode="json")

        assert data == {
            "parent": {
                "type": "page_id",
                "page_id": str(PARENT_PAGE_ID),
            }
        }

    def test_data_source_parent_serialization(self) -> None:
        request = MovePageRequest(
            parent=DataSourceParent(data_source_id=DATA_SOURCE_ID)
        )
        data = request.model_dump(exclude_none=True, mode="json")

        assert data == {
            "parent": {
                "type": "data_source_id",
                "data_source_id": str(DATA_SOURCE_ID),
            }
        }


def _make_page() -> Page:
    from notionary.page.page import Page

    http = AsyncMock()
    http.post = AsyncMock(return_value={"object": "page", "id": str(PAGE_ID)})

    return Page(
        id=PAGE_ID,
        url="https://notion.so/test",
        title="Test Page",
        icon=None,
        cover=None,
        in_trash=False,
        properties={},
        http=http,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=AsyncMock(),
        last_edited_time="2025-01-01T00:00:00.000Z",
        last_edited_by=AsyncMock(),
    )


class TestPageMove:
    @pytest.mark.asyncio
    async def test_move_to_page_calls_post_with_page_parent(self) -> None:
        page = _make_page()
        await page.move_to_page(PARENT_PAGE_ID)

        page._http.post.assert_called_once()
        args, kwargs = page._http.post.call_args
        assert args[0] == f"pages/{PAGE_ID}/move"

        request: MovePageRequest = kwargs.get("data") or args[1]
        assert request.parent.type == "page_id"
        assert request.parent.page_id == PARENT_PAGE_ID

    @pytest.mark.asyncio
    async def test_move_to_data_source_calls_post_with_data_source_parent(self) -> None:
        page = _make_page()
        await page.move_to_data_source(DATA_SOURCE_ID)

        page._http.post.assert_called_once()
        args, kwargs = page._http.post.call_args
        assert args[0] == f"pages/{PAGE_ID}/move"

        request: MovePageRequest = kwargs.get("data") or args[1]
        assert request.parent.type == "data_source_id"
        assert request.parent.data_source_id == DATA_SOURCE_ID
