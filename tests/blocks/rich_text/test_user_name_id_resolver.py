from unittest.mock import AsyncMock

import pytest

from notionary.blocks.rich_text.name_id_resolver.user_name_id_resolver import UserNameIdResolver


@pytest.fixture
def mock_workspace() -> AsyncMock:
    workspace = AsyncMock()
    # Mock user objects
    mock_user1 = AsyncMock()
    mock_user1.id = "user-123"
    mock_user1.name = "John Doe"

    mock_user2 = AsyncMock()
    mock_user2.id = "user-456"
    mock_user2.name = "Jane Smith"

    workspace.search_users.return_value = [mock_user1, mock_user2]
    workspace.get_user_by_id.return_value = mock_user1
    return workspace


@pytest.fixture
def mock_user() -> AsyncMock:
    user = AsyncMock()
    user.id = "user-123"
    user.name = "John Doe"
    return user


@pytest.fixture
def resolver(mock_workspace: AsyncMock) -> UserNameIdResolver:
    return UserNameIdResolver(workspace=mock_workspace)


class TestUserNameIdResolver:
    @pytest.mark.asyncio
    async def test_resolve_user_id_with_empty_name(self, resolver: UserNameIdResolver) -> None:
        result = await resolver.resolve_user_id("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_none(self, resolver: UserNameIdResolver) -> None:
        result = await resolver.resolve_user_id(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_valid_uuid(self, resolver: UserNameIdResolver) -> None:
        uuid_str = "12345678-1234-1234-1234-123456789abc"
        result = await resolver.resolve_user_id(uuid_str)
        assert result == "12345678-1234-1234-1234-123456789abc"

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_name_search(
        self, resolver: UserNameIdResolver, mock_workspace: AsyncMock
    ) -> None:
        result = await resolver.resolve_user_id("John Doe")
        assert result == "user-123"
        mock_workspace.search_users.assert_called_once_with("John Doe")

    @pytest.mark.asyncio
    async def test_resolve_user_id_no_search_results(
        self, resolver: UserNameIdResolver, mock_workspace: AsyncMock
    ) -> None:
        mock_workspace.search_users.return_value = []
        result = await resolver.resolve_user_id("Nonexistent User")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_id_search_exception(
        self, resolver: UserNameIdResolver, mock_workspace: AsyncMock
    ) -> None:
        mock_workspace.search_users.side_effect = Exception("API Error")
        result = await resolver.resolve_user_id("John Doe")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_empty_id(self, resolver: UserNameIdResolver) -> None:
        result = await resolver.resolve_user_name("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_none(self, resolver: UserNameIdResolver) -> None:
        result = await resolver.resolve_user_name(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_invalid_uuid(self, resolver: UserNameIdResolver) -> None:
        result = await resolver.resolve_user_name("invalid-uuid")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_success(
        self, resolver: UserNameIdResolver, mock_workspace: AsyncMock, mock_user: AsyncMock
    ) -> None:
        mock_workspace.get_user_by_id.return_value = mock_user
        result = await resolver.resolve_user_name("12345678-1234-1234-1234-123456789abc")
        assert result == "John Doe"
        mock_workspace.get_user_by_id.assert_called_once_with("12345678-1234-1234-1234-123456789abc")

    @pytest.mark.asyncio
    async def test_resolve_user_name_not_found(self, resolver: UserNameIdResolver, mock_workspace: AsyncMock) -> None:
        mock_workspace.get_user_by_id.return_value = None
        result = await resolver.resolve_user_name("12345678-1234-1234-1234-123456789abc")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_exception(self, resolver: UserNameIdResolver, mock_workspace: AsyncMock) -> None:
        mock_workspace.get_user_by_id.side_effect = Exception("API Error")
        result = await resolver.resolve_user_name("12345678-1234-1234-1234-123456789abc")
        assert result is None

    @pytest.mark.asyncio
    async def test_whitespace_handling(self, resolver: UserNameIdResolver, mock_workspace: AsyncMock) -> None:
        await resolver.resolve_user_id("  John Doe  ")
        mock_workspace.search_users.assert_called_once_with("John Doe")

    @pytest.mark.asyncio
    async def test_fuzzy_matching_best_match(self, resolver: UserNameIdResolver, mock_workspace: AsyncMock) -> None:
        # Mock users with different similarity scores
        user1 = AsyncMock()
        user1.id = "user-123"
        user1.name = "John Doe"

        user2 = AsyncMock()
        user2.id = "user-456"
        user2.name = "John Smith"

        mock_workspace.search_users.return_value = [user1, user2]

        result = await resolver.resolve_user_id("John Doe")
        # Should return the exact match
        assert result == "user-123"

    def test_constructor_with_default_workspace(self) -> None:
        resolver = UserNameIdResolver()
        assert resolver.workspace is not None

    def test_constructor_with_custom_workspace(self, mock_workspace: AsyncMock) -> None:
        resolver = UserNameIdResolver(workspace=mock_workspace)
        assert resolver.workspace == mock_workspace
