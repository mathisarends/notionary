from unittest.mock import AsyncMock, patch

import pytest

from notionary.blocks.rich_text.name_id_resolver.page_name_id_resolver import PageNameIdResolver


@pytest.fixture
def mock_search_client() -> AsyncMock:
    search_client = AsyncMock()
    mock_page = AsyncMock()
    mock_page.id = "page-123"
    mock_page.title = "Test Page"
    search_client.find_page.return_value = mock_page
    return search_client


@pytest.fixture
def mock_page() -> AsyncMock:
    page = AsyncMock()
    page.title = "Test Page"
    return page


@pytest.fixture
def resolver(mock_search_client: AsyncMock) -> PageNameIdResolver:
    return PageNameIdResolver(search_client=mock_search_client, search_limit=10)


class TestPageNameIdResolver:
    @pytest.mark.asyncio
    async def test_resolve_page_id_with_empty_name(self, resolver: PageNameIdResolver) -> None:
        result = await resolver.resolve_name_to_id("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_page_id_with_none(self, resolver: PageNameIdResolver) -> None:
        result = await resolver.resolve_name_to_id(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_page_id_with_valid_uuid(self, resolver: PageNameIdResolver) -> None:
        uuid_str = "12345678-1234-1234-1234-123456789abc"
        result = await resolver.resolve_name_to_id(uuid_str)
        # The resolver now searches by name and returns the actual ID from the search results
        assert result == "page-123"

    @pytest.mark.asyncio
    async def test_resolve_page_id_with_name_search(
        self, resolver: PageNameIdResolver, mock_search_client: AsyncMock
    ) -> None:
        result = await resolver.resolve_name_to_id("Test Page")
        assert result == "page-123"
        mock_search_client.find_page.assert_called_once_with(query="Test Page", limit=10)

    @pytest.mark.asyncio
    async def test_resolve_page_id_no_search_results(
        self, resolver: PageNameIdResolver, mock_search_client: AsyncMock
    ) -> None:
        mock_search_client.find_page.return_value = None
        result = await resolver.resolve_name_to_id("Nonexistent Page")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_page_name_with_empty_id(self, resolver: PageNameIdResolver) -> None:
        result = await resolver.resolve_id_to_name("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_page_name_with_none(self, resolver: PageNameIdResolver) -> None:
        result = await resolver.resolve_id_to_name(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_page_name_success(self, resolver: PageNameIdResolver, mock_page: AsyncMock) -> None:
        with patch("notionary.NotionPage.from_id", return_value=mock_page):
            result = await resolver.resolve_id_to_name("12345678-1234-1234-1234-123456789abc")
            assert result == "Test Page"

    @pytest.mark.asyncio
    async def test_resolve_page_name_not_found(self, resolver: PageNameIdResolver) -> None:
        with patch("notionary.NotionPage.from_id", return_value=None):
            result = await resolver.resolve_id_to_name("12345678-1234-1234-1234-123456789abc")
            assert result is None

    @pytest.mark.asyncio
    async def test_resolve_page_name_exception(self, resolver: PageNameIdResolver) -> None:
        with patch("notionary.NotionPage.from_id", side_effect=Exception("API Error")):
            result = await resolver.resolve_id_to_name("12345678-1234-1234-1234-123456789abc")
            assert result is None

    @pytest.mark.asyncio
    async def test_whitespace_handling(self, resolver: PageNameIdResolver, mock_search_client: AsyncMock) -> None:
        await resolver.resolve_name_to_id("  Test Page  ")
        mock_search_client.find_page.assert_called_once_with(query="Test Page", limit=10)

    def test_constructor_with_default_search_client(self) -> None:
        resolver = PageNameIdResolver()
        assert resolver.search_client is not None
        assert resolver.search_limit == 100

    def test_constructor_with_custom_search_limit(self) -> None:
        resolver = PageNameIdResolver(search_limit=5)
        assert resolver.search_limit == 5
