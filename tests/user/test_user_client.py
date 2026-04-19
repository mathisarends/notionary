from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.user.client import UserClient
from notionary.user.schemas import BotDto, UserType

PERSON_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
BOT_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _person_payload(user_id: UUID = PERSON_ID) -> dict:
    return {
        "id": str(user_id),
        "type": "person",
        "name": "Alice",
        "avatar_url": None,
        "email": "alice@example.com",
    }


def _bot_payload(user_id: UUID = BOT_ID) -> dict:
    return {
        "id": str(user_id),
        "type": "bot",
        "name": "My Bot",
        "avatar_url": None,
        "bot": {
            "owner": {"type": "workspace", "workspace": True},
            "workspace_name": "Acme Corp",
            "workspace_limits": {"max_file_upload_size_in_bytes": 5_000_000},
        },
    }


class TestUserClientGet:
    @pytest.mark.asyncio
    async def test_get_calls_correct_endpoint(self) -> None:
        http = AsyncMock()
        http.get.return_value = _person_payload()
        client = UserClient(http)

        await client.get(PERSON_ID)

        http.get.assert_called_once_with(f"users/{PERSON_ID}")

    @pytest.mark.asyncio
    async def test_get_returns_person_dto(self) -> None:
        http = AsyncMock()
        http.get.return_value = _person_payload()
        client = UserClient(http)

        result = await client.get(PERSON_ID)

        assert result.id == PERSON_ID
        assert result.type == UserType.PERSON

    @pytest.mark.asyncio
    async def test_get_returns_bot_dto(self) -> None:
        http = AsyncMock()
        http.get.return_value = _bot_payload()
        client = UserClient(http)

        result = await client.get(BOT_ID)

        assert result.id == BOT_ID
        assert result.type == UserType.BOT


class TestUserClientList:
    @pytest.mark.asyncio
    async def test_list_calls_paginate(self) -> None:
        http = AsyncMock()
        http.paginate.return_value = []
        client = UserClient(http)

        await client.list()

        http.paginate.assert_called_once_with("users", method="GET", page_size=100)

    @pytest.mark.asyncio
    async def test_list_returns_parsed_dtos(self) -> None:
        http = AsyncMock()
        http.paginate.return_value = [_person_payload(), _bot_payload()]
        client = UserClient(http)

        results = await client.list()

        assert len(results) == 2
        assert results[0].type == UserType.PERSON
        assert results[1].type == UserType.BOT

    @pytest.mark.asyncio
    async def test_list_returns_empty_for_no_users(self) -> None:
        http = AsyncMock()
        http.paginate.return_value = []
        client = UserClient(http)

        results = await client.list()

        assert results == []


class TestUserClientMe:
    @pytest.mark.asyncio
    async def test_me_calls_correct_endpoint(self) -> None:
        http = AsyncMock()
        http.get.return_value = _bot_payload()
        client = UserClient(http)

        await client.me()

        http.get.assert_called_once_with("users/me")

    @pytest.mark.asyncio
    async def test_me_returns_bot_dto(self) -> None:
        http = AsyncMock()
        http.get.return_value = _bot_payload()
        client = UserClient(http)

        result = await client.me()

        assert result.id == BOT_ID
        assert isinstance(result.bot, BotDto)
        assert result.bot.workspace_name == "Acme Corp"
