from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.shared.object.object import NotionObject

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")

_PARTIAL_USER = {"object": "user", "id": str(USER_ID)}
_WORKSPACE_PARENT = {"type": "workspace", "workspace": True}


def _patch_response(
    icon: dict | None = None,
    cover: dict | None = None,
    in_trash: bool = False,
) -> dict:
    return {
        "object": "page",
        "id": str(PAGE_ID),
        "created_time": "2025-01-01T00:00:00.000Z",
        "created_by": _PARTIAL_USER,
        "last_edited_time": "2025-06-01T00:00:00.000Z",
        "last_edited_by": _PARTIAL_USER,
        "cover": cover,
        "icon": icon,
        "parent": _WORKSPACE_PARENT,
        "in_trash": in_trash,
        "url": "https://notion.so/test-page",
    }


def _make_object(in_trash: bool = False) -> tuple[NotionObject, AsyncMock]:
    http = AsyncMock()
    file_uploads = AsyncMock()
    obj = NotionObject(
        icon=None,
        cover=None,
        in_trash=in_trash,
        http_client=http,
        path=f"pages/{PAGE_ID}",
        file_uploads=file_uploads,
    )
    return obj, http


class TestSetIconEmoji:
    @pytest.mark.asyncio
    async def test_set_icon_emoji_calls_patch(self) -> None:
        obj, http = _make_object()
        http.patch.return_value = _patch_response(icon={"type": "emoji", "emoji": "🚀"})

        await obj.set_icon("🚀")

        http.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_icon_emoji_updates_local_state(self) -> None:
        obj, http = _make_object()
        http.patch.return_value = _patch_response(icon={"type": "emoji", "emoji": "🚀"})

        await obj.set_icon("🚀")

        assert obj.icon_emoji == "🚀"
        assert obj.icon_url is None


class TestSetIconUrl:
    @pytest.mark.asyncio
    async def test_set_icon_url_calls_patch(self) -> None:
        obj, http = _make_object()
        icon_dict = {
            "type": "external",
            "external": {"url": "https://example.com/icon.png"},
        }
        http.patch.return_value = _patch_response(icon=icon_dict)

        await obj.set_icon("https://example.com/icon.png")

        http.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_icon_url_updates_local_state(self) -> None:
        obj, http = _make_object()
        icon_dict = {
            "type": "external",
            "external": {"url": "https://example.com/icon.png"},
        }
        http.patch.return_value = _patch_response(icon=icon_dict)

        await obj.set_icon("https://example.com/icon.png")

        assert obj.icon_url == "https://example.com/icon.png"
        assert obj.icon_emoji is None


class TestSetCoverUrl:
    @pytest.mark.asyncio
    async def test_set_cover_url_calls_patch(self) -> None:
        obj, http = _make_object()
        cover_dict = {
            "type": "external",
            "external": {"url": "https://example.com/cover.jpg"},
        }
        http.patch.return_value = _patch_response(cover=cover_dict)

        await obj.set_cover("https://example.com/cover.jpg")

        http.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_cover_url_updates_local_state(self) -> None:
        obj, http = _make_object()
        cover_dict = {
            "type": "external",
            "external": {"url": "https://example.com/cover.jpg"},
        }
        http.patch.return_value = _patch_response(cover=cover_dict)

        await obj.set_cover("https://example.com/cover.jpg")

        assert obj.cover_url == "https://example.com/cover.jpg"


class TestTrashAndRestore:
    @pytest.mark.asyncio
    async def test_trash_sets_in_trash_true(self) -> None:
        obj, http = _make_object(in_trash=False)
        http.patch.return_value = _patch_response(in_trash=True)

        await obj.trash()

        assert obj.in_trash is True

    @pytest.mark.asyncio
    async def test_trash_skips_when_already_in_trash(self) -> None:
        obj, http = _make_object(in_trash=True)

        await obj.trash()

        http.patch.assert_not_called()

    @pytest.mark.asyncio
    async def test_restore_sets_in_trash_false(self) -> None:
        obj, http = _make_object(in_trash=True)
        http.patch.return_value = _patch_response(in_trash=False)

        await obj.restore()

        assert obj.in_trash is False

    @pytest.mark.asyncio
    async def test_restore_skips_when_not_in_trash(self) -> None:
        obj, http = _make_object(in_trash=False)

        await obj.restore()

        http.patch.assert_not_called()
