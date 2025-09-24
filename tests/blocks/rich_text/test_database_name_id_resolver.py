from unittest.mock import AsyncMock, patch

import pytest

from notionary.blocks.rich_text.name_id_resolver.database_name_id_resolver import DatabaseNameIdResolver


@pytest.fixture
def mock_workspace() -> AsyncMock:
    workspace = AsyncMock()
    workspace.search_databases.return_value = [
        AsyncMock(id="db-123", title="Test Database"),
        AsyncMock(id="db-456", title="Another Database"),
    ]
    return workspace


@pytest.fixture
def mock_database() -> AsyncMock:
    database = AsyncMock()
    database.title = "Test Database"
    return database


@pytest.fixture
def resolver(mock_workspace: AsyncMock) -> DatabaseNameIdResolver:
    return DatabaseNameIdResolver(workspace=mock_workspace, search_limit=10)


class TestDatabaseNameIdResolver:
    @pytest.mark.asyncio
    async def test_resolve_database_id_with_empty_name(self, resolver: DatabaseNameIdResolver) -> None:
        result = await resolver.resolve_database_id("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_id_with_none(self, resolver: DatabaseNameIdResolver) -> None:
        result = await resolver.resolve_database_id(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_id_with_search_name(self, resolver: DatabaseNameIdResolver) -> None:
        # Test searches for database name and returns the best match ID
        result = await resolver.resolve_database_id("Test Database")
        assert result == "db-123"

    @pytest.mark.asyncio
    async def test_resolve_database_id_with_name_search(
        self, resolver: DatabaseNameIdResolver, mock_workspace: AsyncMock
    ) -> None:
        result = await resolver.resolve_database_id("Test Database")
        assert result == "db-123"
        mock_workspace.search_databases.assert_called_once_with(query="Test Database", limit=10)

    @pytest.mark.asyncio
    async def test_resolve_database_id_no_search_results(
        self, resolver: DatabaseNameIdResolver, mock_workspace: AsyncMock
    ) -> None:
        mock_workspace.search_databases.return_value = []
        result = await resolver.resolve_database_id("Nonexistent Database")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_with_empty_id(self, resolver: DatabaseNameIdResolver) -> None:
        result = await resolver.resolve_database_name("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_with_none(self, resolver: DatabaseNameIdResolver) -> None:
        result = await resolver.resolve_database_name(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_success(
        self, resolver: DatabaseNameIdResolver, mock_database: AsyncMock
    ) -> None:
        with patch("notionary.NotionDatabase.from_id", return_value=mock_database):
            result = await resolver.resolve_database_name("db-123")
            assert result == "Test Database"

    @pytest.mark.asyncio
    async def test_resolve_database_name_not_found(self, resolver: DatabaseNameIdResolver) -> None:
        with patch("notionary.NotionDatabase.from_id", return_value=None):
            result = await resolver.resolve_database_name("db-123")
            assert result is None

    @pytest.mark.asyncio
    async def test_resolve_database_name_exception(self, resolver: DatabaseNameIdResolver) -> None:
        with patch("notionary.NotionDatabase.from_id", side_effect=Exception("API Error")):
            result = await resolver.resolve_database_name("db-123")
            assert result is None

    @pytest.mark.asyncio
    async def test_whitespace_handling(self, resolver: DatabaseNameIdResolver, mock_workspace: AsyncMock) -> None:
        await resolver.resolve_database_id("  Test Database  ")
        mock_workspace.search_databases.assert_called_once_with(query="Test Database", limit=10)

    def test_constructor_with_default_workspace(self) -> None:
        resolver = DatabaseNameIdResolver()
        assert resolver.workspace is not None
        assert resolver.search_limit == 10

    def test_constructor_with_custom_search_limit(self, mock_workspace: AsyncMock) -> None:
        resolver = DatabaseNameIdResolver(workspace=mock_workspace, search_limit=5)
        assert resolver.search_limit == 5
