from unittest.mock import AsyncMock
from uuid import UUID

from notionary.data_source.mapper import to_data_source
from notionary.data_source.schemas import DataSourceDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.schemas import WorkspaceParent
from notionary.user.schemas import PartialUserDto

DS_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _dto(
    title_text: str = "My Database",
    description_text: str = "",
    properties: dict | None = None,
) -> DataSourceDto:
    title = [RichText.from_plain_text(title_text)] if title_text else []
    description = (
        [RichText.from_plain_text(description_text)] if description_text else []
    )
    return DataSourceDto(
        object="database",
        id=DS_ID,
        url="https://notion.so/test-db",
        title=title,
        description=description,
        properties=properties or {},
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


class TestToDataSource:
    def test_maps_basic_fields(self) -> None:
        http = AsyncMock()
        dto = _dto(title_text="Sales Pipeline")

        ds = to_data_source(dto, http)

        assert ds.id == DS_ID
        assert ds.title == "Sales Pipeline"
        assert ds.url == "https://notion.so/test-db"
        assert ds.in_trash is False
        assert ds.created_time == "2025-01-01T00:00:00.000Z"
        assert ds.last_edited_time == "2025-06-01T00:00:00.000Z"

    def test_empty_description_becomes_none(self) -> None:
        http = AsyncMock()
        dto = _dto(description_text="")

        ds = to_data_source(dto, http)

        assert ds.description is None

    def test_non_empty_description_is_preserved(self) -> None:
        http = AsyncMock()
        dto = _dto(description_text="Tracks all deals")

        ds = to_data_source(dto, http)

        assert ds.description == "Tracks all deals"

    def test_properties_passed_through(self) -> None:
        http = AsyncMock()
        dto = _dto(properties={})

        ds = to_data_source(dto, http)

        assert ds.properties == {}

    def test_created_and_edited_by_forwarded(self) -> None:
        http = AsyncMock()
        dto = _dto()

        ds = to_data_source(dto, http)

        assert ds.created_by.id == USER_ID
        assert ds.last_edited_by.id == USER_ID
