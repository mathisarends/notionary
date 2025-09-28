from unittest.mock import AsyncMock, patch

import pytest

from notionary.blocks.rich_text.name_id_resolver.user_name_id_resolver import UserNameIdResolver


@pytest.fixture
def mock_search_client() -> AsyncMock:
    search_client = AsyncMock()
    # Mock user objects
    mock_user1 = AsyncMock()
    mock_user1.id = "user-123"
    mock_user1.name = "John Doe"

    search_client.find_user.return_value = mock_user1
    return search_client


@pytest.fixture
def mock_user() -> AsyncMock:
    user = AsyncMock()
    user.id = "user-123"
    user.name = "John Doe"
    return user


@pytest.fixture
def resolver(mock_search_client: AsyncMock) -> UserNameIdResolver:
    return UserNameIdResolver(search_client=mock_search_client)


class TestUserNameIdResolver:
    @pytest.mark.asyncio
    async def test_resolve_user_id_with_empty_name(self, mock_search_client: AsyncMock) -> None:
        resolver = UserNameIdResolver(search_client=mock_search_client)
        result = await resolver.resolve_name_to_id("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_none(self, mock_search_client: AsyncMock) -> None:
        resolver = UserNameIdResolver(search_client=mock_search_client)
        result = await resolver.resolve_name_to_id(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_valid_uuid(self, resolver: UserNameIdResolver) -> None:
        uuid_str = "12345678-1234-1234-1234-123456789abc"
        result = await resolver.resolve_name_to_id(uuid_str)
        # The resolver now searches by name and returns the actual ID from the search results
        assert result == "user-123"

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_name_search(
        self, resolver: UserNameIdResolver, mock_search_client: AsyncMock
    ) -> None:
        result = await resolver.resolve_name_to_id("John Doe")
        assert result == "user-123"
        mock_search_client.find_user.assert_called_once_with("John Doe")

    @pytest.mark.asyncio
    async def test_resolve_user_id_no_search_results(
        self, resolver: UserNameIdResolver, mock_search_client: AsyncMock
    ) -> None:
        mock_search_client.find_user.return_value = None
        result = await resolver.resolve_name_to_id("Nonexistent User")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_id_search_exception(self, mock_search_client: AsyncMock) -> None:
        mock_search_client.find_user.side_effect = Exception("API Error")
        resolver = UserNameIdResolver(search_client=mock_search_client)
        result = await resolver.resolve_name_to_id("John Doe")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_empty_id(self, resolver: UserNameIdResolver) -> None:
        result = await resolver.resolve_id_to_name("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_none(self, resolver: UserNameIdResolver) -> None:
        result = await resolver.resolve_id_to_name(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_invalid_uuid(self, resolver: UserNameIdResolver) -> None:
        # Since UUID formatting was removed, invalid UUIDs are now treated as regular search queries
        with patch("notionary.user.notion_user.NotionUser.from_user_id") as mock_from_id:
            mock_user = AsyncMock()
            mock_user.name = "John Doe"
            mock_from_id.return_value = mock_user
            result = await resolver.resolve_id_to_name("invalid-uuid")
            assert result == "John Doe"

    @pytest.mark.asyncio
    async def test_resolve_user_name_success(self, resolver: UserNameIdResolver, mock_user: AsyncMock) -> None:
        with patch("notionary.user.notion_user.NotionUser.from_user_id", return_value=mock_user):
            result = await resolver.resolve_id_to_name("12345678-1234-1234-1234-123456789abc")
            assert result == "John Doe"

    @pytest.mark.asyncio
    async def test_resolve_user_name_not_found(self, resolver: UserNameIdResolver) -> None:
        with patch("notionary.user.notion_user.NotionUser.from_user_id", return_value=None):
            result = await resolver.resolve_id_to_name("12345678-1234-1234-1234-123456789abc")
            assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_exception(self, resolver: UserNameIdResolver) -> None:
        with patch("notionary.user.notion_user.NotionUser.from_user_id", side_effect=Exception("API Error")):
            result = await resolver.resolve_id_to_name("12345678-1234-1234-1234-123456789abc")
            assert result is None

    @pytest.mark.asyncio
    async def test_whitespace_handling(self, mock_search_client: AsyncMock) -> None:
        resolver = UserNameIdResolver(search_client=mock_search_client)
        await resolver.resolve_name_to_id("  John Doe  ")
        mock_search_client.find_user.assert_called_once_with("John Doe")

    def test_constructor_with_default_search_client(self) -> None:
        resolver = UserNameIdResolver()
        assert resolver._search_client is not None

    def test_constructor_with_custom_search_client(self, mock_search_client: AsyncMock) -> None:
        resolver = UserNameIdResolver(search_client=mock_search_client)
        assert resolver._search_client == mock_search_client
