from unittest.mock import AsyncMock
from uuid import UUID

from notionary.database.mapper import to_database
from notionary.database.schemas import DatabaseDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.schemas import WorkspaceParent
from notionary.user.schemas import PartialUserDto

DB_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _dto(
    title_text: str = "My Database",
    description_text: str = "",
    is_inline: bool = False,
    is_locked: bool = False,
) -> DatabaseDto:
    title = [RichText.from_plain_text(title_text)] if title_text else []
    description = (
        [RichText.from_plain_text(description_text)] if description_text else []
    )
    return DatabaseDto(
        object="database",
        id=DB_ID,
        url="https://notion.so/test-db",
        title=title,
        description=description,
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


class TestToDatabase:
    def test_maps_basic_fields(self) -> None:
        http = AsyncMock()
        dto = _dto(title_text="Sales Pipeline")

        db = to_database(dto, http)

        assert db.id == DB_ID
        assert db.title == "Sales Pipeline"
        assert db.url == "https://notion.so/test-db"
        assert db.in_trash is False
        assert db.created_time == "2025-01-01T00:00:00.000Z"
        assert db.last_edited_time == "2025-06-01T00:00:00.000Z"

    def test_empty_description_becomes_none(self) -> None:
        http = AsyncMock()
        dto = _dto(description_text="")

        db = to_database(dto, http)

        assert db.description is None

    def test_non_empty_description_is_preserved(self) -> None:
        http = AsyncMock()
        dto = _dto(description_text="Tracks all deals")

        db = to_database(dto, http)

        assert db.description == "Tracks all deals"

    def test_is_inline_forwarded(self) -> None:
        http = AsyncMock()
        dto = _dto(is_inline=True)

        db = to_database(dto, http)

        assert db.is_inline is True

    def test_is_locked_forwarded(self) -> None:
        http = AsyncMock()
        dto = _dto(is_locked=True)

        db = to_database(dto, http)

        assert db.is_locked is True

    def test_created_and_edited_by_forwarded(self) -> None:
        http = AsyncMock()
        dto = _dto()

        db = to_database(dto, http)

        assert db.created_by.id == USER_ID
        assert db.last_edited_by.id == USER_ID

    def test_data_sources_empty_by_default(self) -> None:
        http = AsyncMock()
        dto = _dto()

        db = to_database(dto, http)

        assert db.data_sources == []
