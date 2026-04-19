from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.user.models import Bot, Person
from notionary.user.namespace import UsersNamespace
from notionary.user.schemas import (
    BotDto,
    BotResponseDto,
    PersonResponseDto,
    WorkspaceLimits,
)

PERSON_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
BOT_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _person_dto(
    name: str = "Alice", email: str = "alice@example.com"
) -> PersonResponseDto:
    return PersonResponseDto(id=PERSON_ID, name=name, email=email)


def _bot_dto(name: str = "My Bot") -> BotResponseDto:
    limits = WorkspaceLimits(max_file_upload_size_in_bytes=5_000_000)
    bot = BotDto(workspace_name="Acme", workspace_limits=limits)
    return BotResponseDto(id=BOT_ID, name=name, bot=bot)


def _make_namespace() -> tuple[UsersNamespace, AsyncMock]:
    http = AsyncMock()
    ns = UsersNamespace(http)
    return ns, http


class TestUsersNamespaceList:
    @pytest.mark.asyncio
    async def test_list_returns_all_users_when_no_filter(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(return_value=[_person_dto(), _bot_dto()])

        results = await ns.list()

        assert len(results) == 2
        assert any(isinstance(r, Person) for r in results)
        assert any(isinstance(r, Bot) for r in results)

    @pytest.mark.asyncio
    async def test_list_filters_to_persons_only(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(return_value=[_person_dto(), _bot_dto()])

        results = await ns.list(filter="person")

        assert len(results) == 1
        assert isinstance(results[0], Person)

    @pytest.mark.asyncio
    async def test_list_filters_to_bots_only(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(return_value=[_person_dto(), _bot_dto()])

        results = await ns.list(filter="bot")

        assert len(results) == 1
        assert isinstance(results[0], Bot)

    @pytest.mark.asyncio
    async def test_list_returns_empty_when_no_users(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(return_value=[])

        results = await ns.list()

        assert results == []


class TestUsersNamespaceSearch:
    @pytest.mark.asyncio
    async def test_search_matches_by_name_case_insensitive(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(
            return_value=[
                _person_dto(name="Alice", email="alice@example.com"),
                _person_dto(name="Bob", email="bob@example.com"),
            ]
        )

        results = await ns.search("alice")

        assert len(results) == 1
        assert results[0].name == "Alice"

    @pytest.mark.asyncio
    async def test_search_matches_by_email(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(
            return_value=[
                _person_dto(email="alice@example.com"),
                _person_dto(email="bob@example.com"),
            ]
        )

        results = await ns.search("alice@example")

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_search_returns_empty_when_no_match(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(return_value=[_person_dto(name="Alice")])

        results = await ns.search("zzz_no_match")

        assert results == []

    @pytest.mark.asyncio
    async def test_search_with_person_filter(self) -> None:
        ns, _ = _make_namespace()
        ns._client.list = AsyncMock(
            return_value=[_person_dto(name="Alice"), _bot_dto(name="Alice Bot")]
        )

        results = await ns.search("alice", filter="person")

        assert all(isinstance(r, Person) for r in results)


class TestUsersNamespaceMe:
    @pytest.mark.asyncio
    async def test_me_returns_bot(self) -> None:
        ns, _ = _make_namespace()
        ns._client.me = AsyncMock(return_value=_bot_dto())

        result = await ns.me()

        assert isinstance(result, Bot)
        assert result.id == BOT_ID
