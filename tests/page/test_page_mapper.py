from unittest.mock import AsyncMock
from uuid import UUID

from notionary.page.mapper import to_page
from notionary.page.properties.schemas import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.schemas import WorkspaceParent
from notionary.user.schemas import PartialUserDto

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _dto(
    title: str = "My Page",
    properties: dict | None = None,
) -> PageDto:
    if properties is None:
        properties = {
            "Name": PageTitleProperty(title=[RichText.from_plain_text(title)]),
        }
    return PageDto(
        object="page",
        id=PAGE_ID,
        url="https://notion.so/test-page",
        properties=properties,
        parent=WorkspaceParent(type="workspace", workspace=True),
        icon=None,
        cover=None,
        in_trash=False,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


class TestToPage:
    def test_maps_basic_fields(self) -> None:
        http = AsyncMock()
        dto = _dto(title="Sprint Planning")

        page = to_page(dto, http)

        assert page.id == PAGE_ID
        assert page.title == "Sprint Planning"
        assert page.url == "https://notion.so/test-page"
        assert page.in_trash is False
        assert page.created_time == "2025-01-01T00:00:00.000Z"
        assert page.last_edited_time == "2025-06-01T00:00:00.000Z"

    def test_missing_title_property_results_in_empty_title(self) -> None:
        http = AsyncMock()
        dto = _dto(properties={})

        page = to_page(dto, http)

        assert page.title == ""

    def test_created_and_edited_by_forwarded(self) -> None:
        http = AsyncMock()
        dto = _dto()

        page = to_page(dto, http)

        assert page.created_by.id == USER_ID
        assert page.last_edited_by.id == USER_ID

    def test_properties_passed_through(self) -> None:
        http = AsyncMock()
        title_prop = PageTitleProperty(title=[RichText.from_plain_text("Test")])
        dto = _dto(properties={"Name": title_prop})

        page = to_page(dto, http)

        assert "Name" in page.properties.properties
