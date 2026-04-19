from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.properties import PageProperties
from notionary.page.properties.schemas import (
    DateValue,
    PageCheckboxProperty,
    PageDateProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    RelationItem,
    SelectOption,
    StatusOption,
)
from notionary.rich_text.schemas import RichText

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")

_STATUS_OPTIONS = [
    StatusOption(id="1", name="Not started"),
    StatusOption(id="2", name="In progress"),
    StatusOption(id="3", name="Done"),
]

_SELECT_OPTIONS = [
    SelectOption(id="1", name="High"),
    SelectOption(id="2", name="Medium"),
    SelectOption(id="3", name="Low"),
]


def _make_service(properties: dict) -> PageProperties:
    http = AsyncMock()
    service = PageProperties(id=PAGE_ID, properties=properties, http=http)
    return service


def _stub_set_property(service: PageProperties) -> AsyncMock:
    mock = AsyncMock(return_value=type("Dto", (), {"properties": service.properties})())
    service._property_http_client.set_property = mock
    return mock


# ============================================================================
# describe()
# ============================================================================


class TestDescribe:
    def test_status_property_with_current_value(self) -> None:
        props = {
            "Status": PageStatusProperty(
                id="s",
                status=StatusOption(id="2", name="In progress"),
                options=_STATUS_OPTIONS,
            )
        }
        result = _make_service(props).describe()

        assert result["Status"]["type"] == "status"
        assert result["Status"]["current"] == "In progress"
        assert result["Status"]["options"] == ["Not started", "In progress", "Done"]

    def test_status_property_without_current_value(self) -> None:
        props = {
            "Status": PageStatusProperty(
                id="s",
                status=None,
                options=_STATUS_OPTIONS,
            )
        }
        result = _make_service(props).describe()

        assert result["Status"]["current"] is None
        assert result["Status"]["options"] == ["Not started", "In progress", "Done"]

    def test_select_property(self) -> None:
        props = {
            "Priority": PageSelectProperty(
                id="p",
                select=SelectOption(id="1", name="High"),
                options=_SELECT_OPTIONS,
            )
        }
        result = _make_service(props).describe()

        assert result["Priority"]["type"] == "select"
        assert result["Priority"]["current"] == "High"
        assert result["Priority"]["options"] == ["High", "Medium", "Low"]

    def test_multi_select_property(self) -> None:
        props = {
            "Tags": PageMultiSelectProperty(
                id="t",
                multi_select=[SelectOption(name="A"), SelectOption(name="B")],
                options=[
                    SelectOption(name="A"),
                    SelectOption(name="B"),
                    SelectOption(name="C"),
                ],
            )
        }
        result = _make_service(props).describe()

        assert result["Tags"]["type"] == "multi_select"
        assert result["Tags"]["current"] == ["A", "B"]
        assert result["Tags"]["options"] == ["A", "B", "C"]

    def test_number_property(self) -> None:
        props = {"Score": PageNumberProperty(id="n", number=42.0)}
        result = _make_service(props).describe()

        assert result["Score"]["type"] == "number"
        assert result["Score"]["current"] == 42.0

    def test_checkbox_property(self) -> None:
        props = {"Done": PageCheckboxProperty(id="c", checkbox=True)}
        result = _make_service(props).describe()

        assert result["Done"]["type"] == "checkbox"
        assert result["Done"]["current"] is True

    def test_date_property(self) -> None:
        props = {"Due": PageDateProperty(id="d", date=DateValue(start="2025-06-01"))}
        result = _make_service(props).describe()

        assert result["Due"]["type"] == "date"
        assert result["Due"]["current"] == "2025-06-01"

    def test_title_property(self) -> None:
        rt = RichText(type="text", plain_text="My Page", text={"content": "My Page"})
        props = {"Name": PageTitleProperty(id="t", title=[rt])}
        result = _make_service(props).describe()

        assert result["Name"]["type"] == "title"
        assert result["Name"]["current"] == "My Page"

    def test_rich_text_property(self) -> None:
        rt = RichText(
            type="text", plain_text="Notes here", text={"content": "Notes here"}
        )
        props = {"Notes": PageRichTextProperty(id="r", rich_text=[rt])}
        result = _make_service(props).describe()

        assert result["Notes"]["type"] == "rich_text"
        assert result["Notes"]["current"] == "Notes here"

    def test_relation_property_includes_current_ids_as_options(self) -> None:
        props = {
            "Module": PageRelationProperty(
                id="rel",
                relation=[
                    RelationItem(id="11111111-1111-1111-1111-111111111111"),
                    RelationItem(id="22222222-2222-2222-2222-222222222222"),
                ],
            )
        }
        result = _make_service(props).describe()

        assert result["Module"]["type"] == "relation"
        assert result["Module"]["current"] == [
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
        ]
        assert result["Module"]["options"] == [
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
        ]

    def test_empty_properties(self) -> None:
        result = _make_service({}).describe()
        assert result == {}


# ============================================================================
# set() — happy paths
# ============================================================================


class TestSetHappyPath:
    @pytest.mark.asyncio
    async def test_set_status(self) -> None:
        props = {
            "Status": PageStatusProperty(id="s", status=None, options=_STATUS_OPTIONS)
        }
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Status", "Done")

        mock.assert_called_once_with("Status", "Done")

    @pytest.mark.asyncio
    async def test_set_select(self) -> None:
        props = {
            "Priority": PageSelectProperty(id="p", select=None, options=_SELECT_OPTIONS)
        }
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Priority", "High")

        mock.assert_called_once_with("Priority", "High")

    @pytest.mark.asyncio
    async def test_set_multi_select_single_string(self) -> None:
        props = {
            "Tags": PageMultiSelectProperty(
                id="t",
                multi_select=[],
                options=[SelectOption(name="A"), SelectOption(name="B")],
            )
        }
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Tags", "A")

        mock.assert_called_once_with("Tags", ["A"])

    @pytest.mark.asyncio
    async def test_set_multi_select_list(self) -> None:
        props = {
            "Tags": PageMultiSelectProperty(
                id="t",
                multi_select=[],
                options=[SelectOption(name="A"), SelectOption(name="B")],
            )
        }
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Tags", ["A", "B"])

        mock.assert_called_once_with("Tags", ["A", "B"])

    @pytest.mark.asyncio
    async def test_set_number(self) -> None:
        props = {"Score": PageNumberProperty(id="n", number=0)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Score", 75)

        mock.assert_called_once_with("Score", 75)

    @pytest.mark.asyncio
    async def test_set_checkbox(self) -> None:
        props = {"Done": PageCheckboxProperty(id="c", checkbox=False)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Done", True)

        mock.assert_called_once_with("Done", True)

    @pytest.mark.asyncio
    async def test_set_date(self) -> None:
        props = {"Due": PageDateProperty(id="d", date=None)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Due", "2025-12-31")

        mock.assert_called_once_with("Due", "2025-12-31")

    @pytest.mark.asyncio
    async def test_set_title(self) -> None:
        props = {"Name": PageTitleProperty(id="t", title=[])}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Name", "New Title")

        mock.assert_called_once_with("Name", "New Title")

    @pytest.mark.asyncio
    async def test_set_relation_single_id(self) -> None:
        props = {
            "Module": PageRelationProperty(
                id="rel",
                relation=[],
            )
        }
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Module", "11111111-1111-1111-1111-111111111111")

        mock.assert_called_once_with("Module", ["11111111-1111-1111-1111-111111111111"])

    @pytest.mark.asyncio
    async def test_set_relation_list_of_ids(self) -> None:
        props = {
            "Module": PageRelationProperty(
                id="rel",
                relation=[],
            )
        }
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set(
            "Module",
            [
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
        )

        mock.assert_called_once_with(
            "Module",
            [
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
        )


# ============================================================================
# set() — validation errors
# ============================================================================


class TestSetValidationErrors:
    @pytest.mark.asyncio
    async def test_unknown_property_name(self) -> None:
        service = _make_service({})

        with pytest.raises(ValueError, match="Unknown property"):
            await service.set("Nonexistent", "value")

    @pytest.mark.asyncio
    async def test_invalid_status_option(self) -> None:
        props = {
            "Status": PageStatusProperty(id="s", status=None, options=_STATUS_OPTIONS)
        }
        service = _make_service(props)

        with pytest.raises(ValueError, match="not a valid option"):
            await service.set("Status", "Fertig")

    @pytest.mark.asyncio
    async def test_invalid_select_option(self) -> None:
        props = {
            "Priority": PageSelectProperty(id="p", select=None, options=_SELECT_OPTIONS)
        }
        service = _make_service(props)

        with pytest.raises(ValueError, match="not a valid option"):
            await service.set("Priority", "Critical")

    @pytest.mark.asyncio
    async def test_invalid_multi_select_option(self) -> None:
        props = {
            "Tags": PageMultiSelectProperty(
                id="t",
                multi_select=[],
                options=[SelectOption(name="A")],
            )
        }
        service = _make_service(props)

        with pytest.raises(ValueError, match="not a valid option"):
            await service.set("Tags", ["A", "Z"])

    @pytest.mark.asyncio
    async def test_status_wrong_type(self) -> None:
        props = {
            "Status": PageStatusProperty(id="s", status=None, options=_STATUS_OPTIONS)
        }
        service = _make_service(props)

        with pytest.raises(TypeError, match="expects a string"):
            await service.set("Status", 123)

    @pytest.mark.asyncio
    async def test_number_wrong_type(self) -> None:
        props = {"Score": PageNumberProperty(id="n", number=0)}
        service = _make_service(props)

        with pytest.raises(TypeError, match="expects a number"):
            await service.set("Score", "not a number")

    @pytest.mark.asyncio
    async def test_checkbox_wrong_type(self) -> None:
        props = {"Done": PageCheckboxProperty(id="c", checkbox=False)}
        service = _make_service(props)

        with pytest.raises(TypeError, match="expects a bool"):
            await service.set("Done", "yes")

    @pytest.mark.asyncio
    async def test_date_wrong_type(self) -> None:
        props = {"Due": PageDateProperty(id="d", date=None)}
        service = _make_service(props)

        with pytest.raises(TypeError, match="expects an ISO date string"):
            await service.set("Due", 20250101)

    @pytest.mark.asyncio
    async def test_title_wrong_type(self) -> None:
        props = {"Name": PageTitleProperty(id="t", title=[])}
        service = _make_service(props)

        with pytest.raises(TypeError, match="expects a string"):
            await service.set("Name", 42)

    @pytest.mark.asyncio
    async def test_error_message_includes_valid_options(self) -> None:
        props = {
            "Status": PageStatusProperty(id="s", status=None, options=_STATUS_OPTIONS)
        }
        service = _make_service(props)

        with pytest.raises(ValueError, match=r"Not started.*In progress.*Done"):
            await service.set("Status", "Invalid")

    @pytest.mark.asyncio
    async def test_relation_wrong_container_type_includes_available_ids(self) -> None:
        props = {
            "Module": PageRelationProperty(
                id="rel",
                relation=[RelationItem(id="11111111-1111-1111-1111-111111111111")],
            )
        }
        service = _make_service(props)

        with pytest.raises(TypeError, match=r"Available relation ids: .*11111111"):
            await service.set("Module", 123)

    @pytest.mark.asyncio
    async def test_relation_non_string_item_includes_available_ids(self) -> None:
        props = {
            "Module": PageRelationProperty(
                id="rel",
                relation=[RelationItem(id="11111111-1111-1111-1111-111111111111")],
            )
        }
        service = _make_service(props)

        with pytest.raises(TypeError, match=r"Available relation ids: .*11111111"):
            await service.set("Module", ["11111111-1111-1111-1111-111111111111", 7])

    @pytest.mark.asyncio
    async def test_relation_invalid_id_includes_available_ids(self) -> None:
        props = {
            "Module": PageRelationProperty(
                id="rel",
                relation=[RelationItem(id="11111111-1111-1111-1111-111111111111")],
            )
        }
        service = _make_service(props)

        with pytest.raises(
            ValueError,
            match=r"not a valid relation page id.*Available relation ids: .*11111111",
        ):
            await service.set("Module", "not-a-page-id")
