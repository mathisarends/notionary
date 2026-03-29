from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.page import Page

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
PARENT_PAGE_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
DS_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _make_page(
    title: str = "Test Page",
    in_trash: bool = False,
) -> Page:
    http = AsyncMock()
    http.patch = AsyncMock(return_value={})
    http.post = AsyncMock(return_value={"object": "page", "id": str(PAGE_ID)})
    return Page(
        id=PAGE_ID,
        url="https://notion.so/test",
        title=title,
        icon=None,
        cover=None,
        in_trash=in_trash,
        properties={},
        http=http,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=AsyncMock(id=USER_ID),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=AsyncMock(id=USER_ID),
    )


class TestPageProperties:
    def test_in_trash_reflects_initial_state(self) -> None:
        page = _make_page(in_trash=False)
        assert page.in_trash is False

    def test_in_trash_true(self) -> None:
        page = _make_page(in_trash=True)
        assert page.in_trash is True

    def test_str_contains_title_and_url(self) -> None:
        page = _make_page(title="My Page")
        assert str(page) == "My Page (https://notion.so/test)"

    def test_repr_contains_id_and_title(self) -> None:
        page = _make_page(title="My Page")
        assert "My Page" in repr(page)
        assert str(PAGE_ID) in repr(page)


class TestPageTrash:
    @pytest.mark.asyncio
    async def test_trash_delegates_to_object(self) -> None:
        page = _make_page()
        page._object.trash = AsyncMock()

        await page.trash()

        page._object.trash.assert_called_once()

    @pytest.mark.asyncio
    async def test_restore_delegates_to_object(self) -> None:
        page = _make_page(in_trash=True)
        page._object.restore = AsyncMock()

        await page.restore()

        page._object.restore.assert_called_once()


class TestPageRename:
    @pytest.mark.asyncio
    async def test_rename_updates_title(self) -> None:
        page = _make_page(title="Old Title")
        page.properties.set_title = AsyncMock()

        await page.rename("New Title")

        page.properties.set_title.assert_called_once_with("New Title")
        assert page.title == "New Title"


class TestPageLocking:
    @pytest.mark.asyncio
    async def test_lock_calls_patch(self) -> None:
        page = _make_page()
        await page.lock()

        page._http.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_unlock_calls_patch(self) -> None:
        page = _make_page()
        await page.unlock()

        page._http.patch.assert_called_once()


class TestPageContent:
    @pytest.mark.asyncio
    async def test_append_delegates_to_content(self) -> None:
        page = _make_page()
        page._content.append = AsyncMock()

        await page.append("# Hello")

        page._content.append.assert_called_once_with(content="# Hello")

    @pytest.mark.asyncio
    async def test_replace_delegates_to_content(self) -> None:
        page = _make_page()
        page._content.replace = AsyncMock()

        await page.replace("New content")

        page._content.replace.assert_called_once_with(content="New content")

    @pytest.mark.asyncio
    async def test_clear_delegates_to_content(self) -> None:
        page = _make_page()
        page._content.clear = AsyncMock()

        await page.clear()

        page._content.clear.assert_called_once()


class TestPageComments:
    @pytest.mark.asyncio
    async def test_comment_delegates_to_comments_service(self) -> None:
        page = _make_page()
        page._comments.create = AsyncMock()

        await page.comment("Great work!")

        page._comments.create.assert_called_once_with("Great work!")


class TestPageUpdate:
    @pytest.mark.asyncio
    async def test_update_only_sets_provided_fields(self) -> None:
        page = _make_page()
        page.properties.set_title = AsyncMock()
        page._content.replace = AsyncMock()
        page._content.append = AsyncMock()
        page._object.update = AsyncMock()

        await page.update(title="New")

        page.properties.set_title.assert_called_once_with("New")
        assert page.title == "New"
        page._content.replace.assert_not_called()
        page._content.append.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_with_content_calls_replace(self) -> None:
        page = _make_page()
        page._content.replace = AsyncMock()
        page._object.update = AsyncMock()

        await page.update(content="replaced")

        page._content.replace.assert_called_once_with(content="replaced")

    @pytest.mark.asyncio
    async def test_update_with_append_content(self) -> None:
        page = _make_page()
        page._content.append = AsyncMock()
        page._object.update = AsyncMock()

        await page.update(append_content="appended")

        page._content.append.assert_called_once_with(content="appended")

    @pytest.mark.asyncio
    async def test_content_takes_precedence_over_append(self) -> None:
        page = _make_page()
        page._content.replace = AsyncMock()
        page._content.append = AsyncMock()
        page._object.update = AsyncMock()

        await page.update(content="full", append_content="extra")

        page._content.replace.assert_called_once()
        page._content.append.assert_not_called()
