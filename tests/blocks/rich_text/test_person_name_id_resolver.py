from unittest.mock import AsyncMock

import pytest

from notionary.rich_text.name_id_resolver.person import PersonNameIdResolver


@pytest.fixture
def mock_person_factory() -> AsyncMock:
    factory = AsyncMock()
    # Mock user objects
    mock_user1 = AsyncMock()
    mock_user1.id = "user-123"
    mock_user1.name = "John Doe"

    factory.from_name.return_value = mock_user1
    factory.from_id.return_value = mock_user1
    return factory


@pytest.fixture
def mock_user() -> AsyncMock:
    user = AsyncMock()
    user.id = "user-123"
    user.name = "John Doe"
    return user


@pytest.fixture
def resolver(mock_person_factory: AsyncMock) -> PersonNameIdResolver:
    return PersonNameIdResolver(person_user_factory=mock_person_factory)


class TestUserNameIdResolver:
    @pytest.mark.asyncio
    async def test_resolve_user_id_with_empty_name(
        self, mock_person_factory: AsyncMock
    ) -> None:
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        result = await resolver.resolve_name_to_id("")
        assert result is None
        mock_person_factory.from_name.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_none(
        self, mock_person_factory: AsyncMock
    ) -> None:
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        result = await resolver.resolve_name_to_id(None)
        assert result is None
        mock_person_factory.from_name.assert_not_called()

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_valid_uuid(
        self, resolver: PersonNameIdResolver
    ) -> None:
        result = await resolver.resolve_name_to_id(
            "12345678-1234-1234-1234-123456789abc"
        )
        assert result == "user-123"

    @pytest.mark.asyncio
    async def test_resolve_user_id_with_name_search(
        self, resolver: PersonNameIdResolver
    ) -> None:
        result = await resolver.resolve_name_to_id("John Doe")
        assert result == "user-123"

    @pytest.mark.asyncio
    async def test_resolve_user_id_no_search_results(
        self, mock_person_factory: AsyncMock
    ) -> None:
        mock_person_factory.from_name.side_effect = ValueError("No user found")
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        result = await resolver.resolve_name_to_id("Nonexistent User")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_id_search_exception(
        self, mock_person_factory: AsyncMock
    ) -> None:
        mock_person_factory.from_name.side_effect = Exception("API Error")
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        result = await resolver.resolve_name_to_id("John Doe")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_empty_id(
        self, resolver: PersonNameIdResolver
    ) -> None:
        result = await resolver.resolve_id_to_name("")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_none(
        self, resolver: PersonNameIdResolver
    ) -> None:
        result = await resolver.resolve_id_to_name(None)
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_with_invalid_uuid(
        self, mock_person_factory: AsyncMock
    ) -> None:
        mock_person_factory.from_id.side_effect = ValueError("Invalid UUID")
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        result = await resolver.resolve_id_to_name("invalid-uuid")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_success(
        self, resolver: PersonNameIdResolver
    ) -> None:
        result = await resolver.resolve_id_to_name(
            "12345678-1234-1234-1234-123456789abc"
        )
        assert result == "John Doe"

    @pytest.mark.asyncio
    async def test_resolve_user_name_not_found(
        self, mock_person_factory: AsyncMock
    ) -> None:
        mock_person_factory.from_id.side_effect = ValueError("User not found")
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        result = await resolver.resolve_id_to_name(
            "12345678-1234-1234-1234-123456789abc"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_user_name_exception(
        self, mock_person_factory: AsyncMock
    ) -> None:
        mock_person_factory.from_id.side_effect = Exception("API Error")
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        result = await resolver.resolve_id_to_name(
            "12345678-1234-1234-1234-123456789abc"
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_whitespace_handling(
        self, resolver: PersonNameIdResolver, mock_person_factory: AsyncMock
    ) -> None:
        await resolver.resolve_name_to_id("  John Doe  ")
        mock_person_factory.from_name.assert_called_once_with("John Doe", None)

    def test_constructor_with_default_search_client(self) -> None:
        resolver = PersonNameIdResolver()
        assert resolver.person_user_factory is not None

    def test_constructor_with_custom_person_factory(
        self, mock_person_factory: AsyncMock
    ) -> None:
        resolver = PersonNameIdResolver(person_user_factory=mock_person_factory)
        assert resolver.person_user_factory == mock_person_factory
