import pytest

from notionary.utils.pagination import PaginatedResponse, paginate_notion_api


@pytest.fixture
def sample_results() -> list[dict[str, str]]:
    return [
        {"id": "1", "name": "Item 1"},
        {"id": "2", "name": "Item 2"},
        {"id": "3", "name": "Item 3"},
    ]


def create_paginated_response(
    results: list[dict], has_more: bool = False, next_cursor: str | None = None
) -> PaginatedResponse:
    return PaginatedResponse(
        results=results,
        has_more=has_more,
        next_cursor=next_cursor,
    )


def create_mock_api_with_pages(pages: list[PaginatedResponse]):
    call_count = 0

    async def mock_api(**kwargs) -> PaginatedResponse:  # pylint: disable=invalid-overridden-method
        nonlocal call_count
        if call_count >= len(pages):
            raise ValueError(f"Unexpected call {call_count + 1}, only {len(pages)} pages defined")

        response = pages[call_count]
        call_count += 1
        return response

    return mock_api


# ============================================================================
# Tests
# ============================================================================


@pytest.mark.asyncio
async def test_single_page_pagination(sample_results: list[dict[str, str]]) -> None:
    single_page = create_paginated_response(
        results=sample_results,
        has_more=False,
        next_cursor=None,
    )

    mock_api = create_mock_api_with_pages([single_page])
    results = await paginate_notion_api(mock_api, block_id="test_block")

    assert len(results) == 3
    assert results == sample_results


@pytest.mark.asyncio
async def test_multiple_pages_pagination() -> None:
    page1 = create_paginated_response(
        results=[{"id": "1"}, {"id": "2"}],
        has_more=True,
        next_cursor="cursor_1",
    )

    page2 = create_paginated_response(
        results=[{"id": "3"}, {"id": "4"}],
        has_more=True,
        next_cursor="cursor_2",
    )

    page3 = create_paginated_response(
        results=[{"id": "5"}],
        has_more=False,
        next_cursor=None,
    )

    mock_api = create_mock_api_with_pages([page1, page2, page3])
    results = await paginate_notion_api(mock_api, block_id="test_block")

    assert len(results) == 5
    assert [r["id"] for r in results] == ["1", "2", "3", "4", "5"]


@pytest.mark.asyncio
async def test_pagination_passes_cursor_correctly() -> None:
    received_kwargs = []

    async def tracking_mock_api(**kwargs) -> PaginatedResponse:
        received_kwargs.append(kwargs.copy())

        if len(received_kwargs) == 1:
            return create_paginated_response(
                results=[{"id": "1"}],
                has_more=True,
                next_cursor="cursor_abc",
            )
        else:
            return create_paginated_response(
                results=[{"id": "2"}],
                has_more=False,
                next_cursor=None,
            )

    await paginate_notion_api(tracking_mock_api, block_id="test_block", page_size=10)

    assert len(received_kwargs) == 2
    assert received_kwargs[0] == {"block_id": "test_block", "page_size": 10}
    assert received_kwargs[1] == {"block_id": "test_block", "page_size": 10, "start_cursor": "cursor_abc"}


@pytest.mark.asyncio
async def test_empty_results_pagination() -> None:
    empty_page = create_paginated_response(
        results=[],
        has_more=False,
        next_cursor=None,
    )

    mock_api = create_mock_api_with_pages([empty_page])
    results = await paginate_notion_api(mock_api)

    assert results == []


@pytest.mark.asyncio
async def test_pagination_with_mixed_empty_pages():
    page1 = create_paginated_response(
        results=[{"id": "1"}],
        has_more=True,
        next_cursor="cursor_1",
    )

    page2 = create_paginated_response(
        results=[],
        has_more=True,
        next_cursor="cursor_2",
    )

    page3 = create_paginated_response(
        results=[{"id": "2"}],
        has_more=False,
        next_cursor=None,
    )

    mock_api = create_mock_api_with_pages([page1, page2, page3])
    results = await paginate_notion_api(mock_api)

    assert len(results) == 2
    assert [r["id"] for r in results] == ["1", "2"]


@pytest.mark.asyncio
async def test_preserves_original_kwargs() -> None:
    original_kwargs = {"block_id": "test", "page_size": 50}

    page = create_paginated_response(
        results=[{"id": "1"}],
        has_more=False,
        next_cursor=None,
    )

    mock_api = create_mock_api_with_pages([page])
    await paginate_notion_api(mock_api, **original_kwargs)

    assert original_kwargs == {"block_id": "test", "page_size": 50}
    assert "start_cursor" not in original_kwargs
