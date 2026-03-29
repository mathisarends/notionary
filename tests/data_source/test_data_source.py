from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.data_source.data_source import DataSource
from notionary.data_source.schemas import DataSourceDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.schemas import WorkspaceParent
from notionary.user.schemas import PartialUserDto

DS_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _make_data_source(
    title: str = "Test DS",
    in_trash: bool = False,
) -> DataSource:
    http = AsyncMock()
    http.patch = AsyncMock(return_value={})
    http.post = AsyncMock(return_value={})
    return DataSource(
        id=DS_ID,
        url="https://notion.so/test-ds",
        title=title,
        description=None,
        icon=None,
        cover=None,
        in_trash=in_trash,
        properties={},
        http=http,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


class TestDataSourceProperties:
    def test_in_trash_reflects_initial_state(self) -> None:
        ds = _make_data_source(in_trash=False)
        assert ds.in_trash is False

    def test_in_trash_true(self) -> None:
        ds = _make_data_source(in_trash=True)
        assert ds.in_trash is True

    def test_str_contains_title_and_url(self) -> None:
        ds = _make_data_source(title="My DS")
        assert str(ds) == "My DS (https://notion.so/test-ds)"

    def test_repr_contains_id_and_title(self) -> None:
        ds = _make_data_source(title="My DS")
        assert "My DS" in repr(ds)
        assert str(DS_ID) in repr(ds)


class TestDataSourceTrash:
    @pytest.mark.asyncio
    async def test_trash_delegates_to_object(self) -> None:
        ds = _make_data_source()
        ds._object.trash = AsyncMock()

        await ds.trash()

        ds._object.trash.assert_called_once()

    @pytest.mark.asyncio
    async def test_restore_delegates_to_object(self) -> None:
        ds = _make_data_source(in_trash=True)
        ds._object.restore = AsyncMock()

        await ds.restore()

        ds._object.restore.assert_called_once()


class TestDataSourceSetTitle:
    @pytest.mark.asyncio
    async def test_set_title_updates_local_title(self) -> None:
        ds = _make_data_source(title="Old Title")
        dto_response = DataSourceDto(
            object="database",
            id=DS_ID,
            url="https://notion.so/test-ds",
            title=[RichText.from_plain_text("New Title")],
            description=[],
            properties={},
            database_parent=WorkspaceParent(type="workspace", workspace=True),
            parent=WorkspaceParent(type="workspace", workspace=True),
            icon=None,
            cover=None,
            in_trash=False,
            created_time="2025-01-01T00:00:00.000Z",
            created_by=_user(),
            last_edited_time="2025-06-01T00:00:00.000Z",
            last_edited_by=_user(),
        )
        ds._client.set_title = AsyncMock(return_value=dto_response)

        await ds.set_title("New Title")

        assert ds.title == "New Title"
        ds._client.set_title.assert_called_once_with("New Title")


class TestDataSourceUpdate:
    @pytest.mark.asyncio
    async def test_update_only_title(self) -> None:
        ds = _make_data_source()
        dto_response = DataSourceDto(
            object="database",
            id=DS_ID,
            url="https://notion.so/test-ds",
            title=[RichText.from_plain_text("New")],
            description=[],
            properties={},
            database_parent=WorkspaceParent(type="workspace", workspace=True),
            parent=WorkspaceParent(type="workspace", workspace=True),
            icon=None,
            cover=None,
            in_trash=False,
            created_time="2025-01-01T00:00:00.000Z",
            created_by=_user(),
            last_edited_time="2025-06-01T00:00:00.000Z",
            last_edited_by=_user(),
        )
        ds._client.set_title = AsyncMock(return_value=dto_response)
        ds._object.update = AsyncMock()

        await ds.update(title="New")

        assert ds.title == "New"

    @pytest.mark.asyncio
    async def test_update_noop_when_nothing_provided(self) -> None:
        ds = _make_data_source(title="Original")
        ds._object.update = AsyncMock()

        await ds.update()

        assert ds.title == "Original"
