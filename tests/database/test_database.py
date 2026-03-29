from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.database.database import Database
from notionary.database.schemas import DatabaseDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.schemas import WorkspaceParent
from notionary.user.schemas import PartialUserDto

DB_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _database_dto_response(
    title: str = "Test DB",
    is_locked: bool = False,
    is_inline: bool = False,
) -> DatabaseDto:
    return DatabaseDto(
        object="database",
        id=DB_ID,
        url="https://notion.so/test-db",
        title=[RichText.from_plain_text(title)],
        description=[],
        is_inline=is_inline,
        is_locked=is_locked,
        data_sources=[],
        parent=WorkspaceParent(type="workspace", workspace=True),
        icon=None,
        cover=None,
        in_trash=False,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


def _make_database(
    title: str = "Test DB",
    in_trash: bool = False,
    is_inline: bool = False,
    is_locked: bool = False,
) -> Database:
    http = AsyncMock()
    http.patch = AsyncMock(
        return_value=_database_dto_response(
            title=title, is_locked=is_locked, is_inline=is_inline
        ).model_dump(mode="json")
    )
    http.post = AsyncMock(return_value={})
    return Database(
        id=DB_ID,
        url="https://notion.so/test-db",
        title=title,
        description=None,
        is_inline=is_inline,
        is_locked=is_locked,
        data_sources=[],
        icon=None,
        cover=None,
        in_trash=in_trash,
        http=http,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


class TestDatabaseProperties:
    def test_in_trash_reflects_initial_state(self) -> None:
        db = _make_database(in_trash=False)
        assert db.in_trash is False

    def test_in_trash_true(self) -> None:
        db = _make_database(in_trash=True)
        assert db.in_trash is True

    def test_str_contains_title_and_url(self) -> None:
        db = _make_database(title="My DB")
        assert str(db) == "My DB (https://notion.so/test-db)"

    def test_repr_contains_id_and_title(self) -> None:
        db = _make_database(title="My DB")
        assert "My DB" in repr(db)
        assert str(DB_ID) in repr(db)


class TestDatabaseTrash:
    @pytest.mark.asyncio
    async def test_trash_calls_patch(self) -> None:
        db = _make_database()
        await db.trash()

        db._http.patch.assert_called_once()
        args = db._http.patch.call_args[0]
        assert args[0] == f"databases/{DB_ID}"

    @pytest.mark.asyncio
    async def test_restore_calls_patch(self) -> None:
        db = _make_database(in_trash=True)
        await db.restore()

        db._http.patch.assert_called_once()


class TestDatabaseSetTitle:
    @pytest.mark.asyncio
    async def test_set_title_updates_local_title(self) -> None:
        db = _make_database(title="Old Title")
        response_dto = _database_dto_response(title="New Title")
        db._http.patch = AsyncMock(return_value=response_dto.model_dump(mode="json"))

        await db.set_title("New Title")

        assert db.title == "New Title"


class TestDatabaseSetDescription:
    @pytest.mark.asyncio
    async def test_set_description_updates_local_description(self) -> None:
        db = _make_database()
        response_dto = _database_dto_response()
        response_data = response_dto.model_dump(mode="json")
        response_data["description"] = [
            RichText.from_plain_text("Updated desc").model_dump(mode="json")
        ]
        db._http.patch = AsyncMock(return_value=response_data)

        await db.set_description("Updated desc")

        assert db.description == "Updated desc"


class TestDatabaseLocking:
    @pytest.mark.asyncio
    async def test_lock_sets_is_locked_from_response(self) -> None:
        db = _make_database(is_locked=False)
        response_dto = _database_dto_response(is_locked=True)
        db._http.patch = AsyncMock(return_value=response_dto.model_dump(mode="json"))

        await db.lock()

        assert db.is_locked is True

    @pytest.mark.asyncio
    async def test_unlock_sets_is_locked_from_response(self) -> None:
        db = _make_database(is_locked=True)
        response_dto = _database_dto_response(is_locked=False)
        db._http.patch = AsyncMock(return_value=response_dto.model_dump(mode="json"))

        await db.unlock()

        assert db.is_locked is False


class TestDatabaseInline:
    @pytest.mark.asyncio
    async def test_set_inline_updates_from_response(self) -> None:
        db = _make_database(is_inline=False)
        response_dto = _database_dto_response(is_inline=True)
        db._http.patch = AsyncMock(return_value=response_dto.model_dump(mode="json"))

        await db.set_inline(True)

        assert db.is_inline is True


class TestDatabaseUpdate:
    @pytest.mark.asyncio
    async def test_update_only_title(self) -> None:
        db = _make_database()
        response_dto = _database_dto_response(title="New")
        db._http.patch = AsyncMock(return_value=response_dto.model_dump(mode="json"))
        db._object.update = AsyncMock()

        await db.update(title="New")

        assert db.title == "New"

    @pytest.mark.asyncio
    async def test_update_noop_when_nothing_provided(self) -> None:
        db = _make_database(title="Original")
        db._object.update = AsyncMock()

        await db.update()

        assert db.title == "Original"
        db._http.patch.assert_not_called()
