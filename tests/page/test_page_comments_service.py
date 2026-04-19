from collections.abc import AsyncGenerator
from datetime import datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.comments.models import Comment
from notionary.page.comments.schemas import CommentDto, PageCommentParent
from notionary.page.comments.service import PageComments
from notionary.rich_text.schemas import RichText

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
COMMENT_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
DISCUSSION_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


def _comment_dto(content: str = "Hello") -> CommentDto:
    return CommentDto(
        id=COMMENT_ID,
        parent=PageCommentParent(page_id=PAGE_ID),
        discussion_id=DISCUSSION_ID,
        created_time=datetime(2025, 1, 1),
        last_edited_time=datetime(2025, 1, 1),
        created_by={"object": "user", "id": str(USER_ID)},
        rich_text=[RichText.from_plain_text(content)],
    )


def _fake_iter(*dtos: CommentDto):
    async def _gen(page_id: UUID) -> AsyncGenerator[CommentDto]:
        for dto in dtos:
            yield dto

    return _gen


def _make_service() -> tuple[PageComments, AsyncMock]:
    http = AsyncMock()
    service = PageComments(page_id=PAGE_ID, http=http)
    return service, http


class TestPageCommentsList:
    @pytest.mark.asyncio
    async def test_list_returns_comments(self) -> None:
        service, _ = _make_service()
        service._client.iter = _fake_iter(_comment_dto("First"), _comment_dto("Second"))
        service._user_client.get = AsyncMock(
            return_value=type("Dto", (), {"name": "Alice"})()
        )

        results = await service.list()

        assert len(results) == 2
        assert all(isinstance(c, Comment) for c in results)

    @pytest.mark.asyncio
    async def test_list_returns_empty_when_no_comments(self) -> None:
        service, _ = _make_service()
        service._client.iter = _fake_iter()

        results = await service.list()

        assert results == []

    @pytest.mark.asyncio
    async def test_list_resolves_author_name(self) -> None:
        service, _ = _make_service()
        service._client.iter = _fake_iter(_comment_dto("Hello"))
        service._user_client.get = AsyncMock(
            return_value=type("Dto", (), {"name": "Bob"})()
        )

        results = await service.list()

        assert results[0].author_name == "Bob"

    @pytest.mark.asyncio
    async def test_list_falls_back_to_unknown_author_on_error(self) -> None:
        service, _ = _make_service()
        service._client.iter = _fake_iter(_comment_dto("Hello"))
        service._user_client.get = AsyncMock(side_effect=Exception("not found"))

        results = await service.list()

        assert results[0].author_name == "Unknown Author"


class TestPageCommentsCreate:
    @pytest.mark.asyncio
    async def test_create_returns_comment(self) -> None:
        service, _ = _make_service()
        service._client.create = AsyncMock(return_value=_comment_dto("New comment"))
        service._user_client.get = AsyncMock(
            return_value=type("Dto", (), {"name": "Alice"})()
        )

        result = await service.create("New comment")

        assert isinstance(result, Comment)
        assert result.content == "New comment"

    @pytest.mark.asyncio
    async def test_create_calls_client_create(self) -> None:
        service, _ = _make_service()
        service._client.create = AsyncMock(return_value=_comment_dto("Text"))
        service._user_client.get = AsyncMock(
            return_value=type("Dto", (), {"name": "Alice"})()
        )

        await service.create("Text")

        service._client.create.assert_called_once()
