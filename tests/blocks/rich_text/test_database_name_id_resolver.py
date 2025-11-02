from unittest.mock import AsyncMock, patch

import pytest

from notionary.shared.name_id_resolver.database import DatabaseNameIdResolver


@pytest.fixture
def mock_search_client() -> AsyncMock:
    search_client = AsyncMock()
    mock_database = AsyncMock()
    mock_database.id = "db-123"
    mock_database.title = "Test Database"
    search_client.find_database.return_value = mock_database
    return search_client


@pytest.fixture
def mock_database() -> AsyncMock:
    database = AsyncMock()
    database.title = "Test Database"
    return database


@pytest.fixture
def resolver(mock_search_client: AsyncMock) -> DatabaseNameIdResolver:
    return DatabaseNameIdResolver(search_service=mock_search_client)


class TestDatabaseNameIdResolver:
    @pytest.mark.asyncio
    async def test_resolve_database_id_with_empty_name(
        self, resolver: DatabaseNameIdResolver
    ) -> None:
        result = await resolver.resolve_name_to_id("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_id_with_none(
        self, resolver: DatabaseNameIdResolver
    ) -> None:
        result = await resolver.resolve_name_to_id(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_id_with_valid_uuid(
        self, resolver: DatabaseNameIdResolver
    ) -> None:
        uuid_str = "12345678-1234-1234-1234-123456789abc"
        result = await resolver.resolve_name_to_id(uuid_str)
        # The resolver now searches by name and returns the actual ID from the search results
        assert result == "db-123"

    @pytest.mark.asyncio
    async def test_resolve_database_id_with_name_search(
        self, resolver: DatabaseNameIdResolver, mock_search_client: AsyncMock
    ) -> None:
        result = await resolver.resolve_name_to_id("Test Database")
        assert result == "db-123"
        mock_search_client.find_database.assert_called_once_with(query="Test Database")

    @pytest.mark.asyncio
    async def test_resolve_database_id_no_search_results(
        self, resolver: DatabaseNameIdResolver, mock_search_client: AsyncMock
    ) -> None:
        mock_search_client.find_database.return_value = None
        result = await resolver.resolve_name_to_id("Nonexistent Database")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_with_empty_id(
        self, resolver: DatabaseNameIdResolver
    ) -> None:
        result = await resolver.resolve_id_to_name("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_with_none(
        self, resolver: DatabaseNameIdResolver
    ) -> None:
        result = await resolver.resolve_id_to_name(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_success(
        self, resolver: DatabaseNameIdResolver, mock_database: AsyncMock
    ) -> None:
        with patch("notionary.NotionDatabase.from_id", return_value=mock_database):
            result = await resolver.resolve_id_to_name(
                "12345678-1234-1234-1234-123456789abc"
            )
            assert result == "Test Database"

    @pytest.mark.asyncio
    async def test_resolve_database_name_not_found(
        self, resolver: DatabaseNameIdResolver
    ) -> None:
        with patch("notionary.NotionDatabase.from_id", return_value=None):
            result = await resolver.resolve_id_to_name(
                "12345678-1234-1234-1234-123456789abc"
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_exception(
        self, resolver: DatabaseNameIdResolver
    ) -> None:
        with patch(
            "notionary.NotionDatabase.from_id", side_effect=Exception("API Error")
        ):
            result = await resolver.resolve_id_to_name(
                "12345678-1234-1234-1234-123456789abc"
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_whitespace_handling(
        self, resolver: DatabaseNameIdResolver, mock_search_client: AsyncMock
    ) -> None:
        await resolver.resolve_name_to_id("  Test Database  ")
        mock_search_client.find_database.assert_called_once_with(query="Test Database")

    @pytest.mark.skip("Requires NOTION_TOKEN environment variable")
    def test_constructor_with_default_search_client(self) -> None:
        resolver = DatabaseNameIdResolver()
        assert resolver.search_service is not None
