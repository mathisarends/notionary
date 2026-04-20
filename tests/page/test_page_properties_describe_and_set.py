from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.properties import PageProperties
from notionary.page.properties.schemas import (
    DateValue,
    PageCheckboxProperty,
    PageDateProperty,
    PageEmailProperty,
    PageMultiSelectProperty,
    PageNumberProperty,
    PagePhoneNumberProperty,
    PageRelationProperty,
    PageRichTextProperty,
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    PageURLProperty,
    RelationItem,
    SelectOption,
    StatusOption,
)
from notionary.rich_text.schemas import RichText

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
DATA_SOURCE_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")

_STATUS_OPTION_NAMES = ["Not started", "In progress", "Done"]
_SELECT_OPTION_NAMES = ["High", "Medium", "Low"]


def _make_service(
    properties: dict,
    data_source_id: UUID | None = None,
) -> PageProperties:
    http = AsyncMock()
    service = PageProperties(
        id=PAGE_ID,
        properties=properties,
        http=http,
        data_source_id=data_source_id,
    )
    return service


def _make_service_with_options(
    properties: dict,
    option_names: dict[str, list[str]],
) -> PageProperties:
    """Return a service with pre-populated data-source option names (no HTTP needed)."""
    service = _make_service(properties)
    service._data_source_option_names = option_names
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
                id="s", status=StatusOption(id="2", name="In progress")
            )
        }
        service = _make_service_with_options(props, {"Status": _STATUS_OPTION_NAMES})

        result = service.describe()

        assert result["Status"]["type"] == "status"
        assert result["Status"]["current"] == "In progress"
        assert result["Status"]["options"] == _STATUS_OPTION_NAMES

    def test_status_property_without_current_value(self) -> None:
        props = {"Status": PageStatusProperty(id="s", status=None)}
        service = _make_service_with_options(props, {"Status": _STATUS_OPTION_NAMES})

        result = service.describe()

        assert result["Status"]["current"] is None
        assert result["Status"]["options"] == _STATUS_OPTION_NAMES

    def test_status_property_no_options_returns_empty_list(self) -> None:
        props = {"Status": PageStatusProperty(id="s", status=StatusOption(name="Done"))}
        result = _make_service(props).describe()

        assert result["Status"]["options"] == []

    def test_select_property(self) -> None:
        props = {
            "Priority": PageSelectProperty(
                id="p", select=SelectOption(id="1", name="High")
            )
        }
        service = _make_service_with_options(props, {"Priority": _SELECT_OPTION_NAMES})

        result = service.describe()

        assert result["Priority"]["type"] == "select"
        assert result["Priority"]["current"] == "High"
        assert result["Priority"]["options"] == _SELECT_OPTION_NAMES

    def test_multi_select_property(self) -> None:
        props = {
            "Tags": PageMultiSelectProperty(
                id="t",
                multi_select=[SelectOption(name="A"), SelectOption(name="B")],
            )
        }
        service = _make_service_with_options(props, {"Tags": ["A", "B", "C"]})

        result = service.describe()

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

    def test_date_property_no_value(self) -> None:
        props = {"Due": PageDateProperty(id="d", date=None)}
        result = _make_service(props).describe()

        assert result["Due"]["current"] is None

    def test_title_property(self) -> None:
        rt = RichText(type="text", plain_text="My Page", text={"content": "My Page"})
        props = {"Name": PageTitleProperty(id="t", title=[rt])}
        result = _make_service(props).describe()

        assert result["Name"]["type"] == "title"
        assert result["Name"]["current"] == "My Page"

    def test_title_property_empty(self) -> None:
        props = {"Name": PageTitleProperty(id="t", title=[])}
        result = _make_service(props).describe()

        assert result["Name"]["current"] is None

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
        props = {"Status": PageStatusProperty(id="s", status=None)}
        service = _make_service_with_options(props, {"Status": _STATUS_OPTION_NAMES})
        mock = _stub_set_property(service)

        await service.set("Status", "Done")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageStatusProperty)
        assert sent.status is not None
        assert sent.status.name == "Done"

    @pytest.mark.asyncio
    async def test_set_select(self) -> None:
        props = {"Priority": PageSelectProperty(id="p", select=None)}
        service = _make_service_with_options(props, {"Priority": _SELECT_OPTION_NAMES})
        mock = _stub_set_property(service)

        await service.set("Priority", "High")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageSelectProperty)
        assert sent.select is not None
        assert sent.select.name == "High"

    @pytest.mark.asyncio
    async def test_set_multi_select_single_string(self) -> None:
        props = {"Tags": PageMultiSelectProperty(id="t", multi_select=[])}
        service = _make_service_with_options(props, {"Tags": ["A", "B"]})
        mock = _stub_set_property(service)

        await service.set("Tags", "A")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageMultiSelectProperty)
        assert [opt.name for opt in sent.multi_select] == ["A"]

    @pytest.mark.asyncio
    async def test_set_multi_select_list(self) -> None:
        props = {"Tags": PageMultiSelectProperty(id="t", multi_select=[])}
        service = _make_service_with_options(props, {"Tags": ["A", "B"]})
        mock = _stub_set_property(service)

        await service.set("Tags", ["A", "B"])

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageMultiSelectProperty)
        assert [opt.name for opt in sent.multi_select] == ["A", "B"]

    @pytest.mark.asyncio
    async def test_set_number(self) -> None:
        props = {"Score": PageNumberProperty(id="n", number=0)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Score", 75)

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageNumberProperty)
        assert sent.number == 75

    @pytest.mark.asyncio
    async def test_set_checkbox(self) -> None:
        props = {"Done": PageCheckboxProperty(id="c", checkbox=False)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Done", True)

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageCheckboxProperty)
        assert sent.checkbox is True

    @pytest.mark.asyncio
    async def test_set_date_string(self) -> None:
        props = {"Due": PageDateProperty(id="d", date=None)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Due", "2025-12-31")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageDateProperty)
        assert sent.date is not None
        assert sent.date.start == "2025-12-31"

    @pytest.mark.asyncio
    async def test_set_date_range_dict(self) -> None:
        props = {"Due": PageDateProperty(id="d", date=None)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Due", {"start": "2025-01-01", "end": "2025-01-07"})

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageDateProperty)
        assert sent.date is not None
        assert sent.date.start == "2025-01-01"
        assert sent.date.end == "2025-01-07"

    @pytest.mark.asyncio
    async def test_set_title(self) -> None:
        props = {"Name": PageTitleProperty(id="t", title=[])}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Name", "New Title")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageTitleProperty)
        assert len(sent.title) == 1
        assert sent.title[0].text is not None
        assert sent.title[0].text.content == "New Title"

    @pytest.mark.asyncio
    async def test_set_url(self) -> None:
        props = {"Link": PageURLProperty(id="u", url=None)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Link", "https://example.com")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageURLProperty)
        assert sent.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_set_email(self) -> None:
        props = {"Email": PageEmailProperty(id="e", email=None)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Email", "hello@example.com")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageEmailProperty)
        assert sent.email == "hello@example.com"

    @pytest.mark.asyncio
    async def test_set_phone_number(self) -> None:
        props = {"Phone": PagePhoneNumberProperty(id="p", phone_number=None)}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Phone", "+49 123 456789")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PagePhoneNumberProperty)
        assert sent.phone_number == "+49 123 456789"

    @pytest.mark.asyncio
    async def test_set_relation_single_id(self) -> None:
        props = {"Module": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set("Module", "11111111-1111-1111-1111-111111111111")

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageRelationProperty)
        assert [item.id for item in sent.relation] == [
            "11111111-1111-1111-1111-111111111111"
        ]

    @pytest.mark.asyncio
    async def test_set_relation_list_of_ids(self) -> None:
        props = {"Module": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props)
        mock = _stub_set_property(service)

        await service.set(
            "Module",
            [
                "11111111-1111-1111-1111-111111111111",
                "22222222-2222-2222-2222-222222222222",
            ],
        )

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageRelationProperty)
        assert [item.id for item in sent.relation] == [
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
        ]


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
        props = {"Status": PageStatusProperty(id="s", status=None)}
        service = _make_service_with_options(props, {"Status": _STATUS_OPTION_NAMES})

        with pytest.raises(ValueError, match="not a valid option"):
            await service.set("Status", "Fertig")

    @pytest.mark.asyncio
    async def test_invalid_select_option(self) -> None:
        props = {"Priority": PageSelectProperty(id="p", select=None)}
        service = _make_service_with_options(props, {"Priority": _SELECT_OPTION_NAMES})

        with pytest.raises(ValueError, match="not a valid option"):
            await service.set("Priority", "Critical")

    @pytest.mark.asyncio
    async def test_invalid_multi_select_option(self) -> None:
        props = {"Tags": PageMultiSelectProperty(id="t", multi_select=[])}
        service = _make_service_with_options(props, {"Tags": ["A"]})

        with pytest.raises(ValueError, match="not a valid option"):
            await service.set("Tags", ["A", "Z"])

    @pytest.mark.asyncio
    async def test_status_wrong_type(self) -> None:
        props = {"Status": PageStatusProperty(id="s", status=None)}
        service = _make_service_with_options(props, {"Status": _STATUS_OPTION_NAMES})

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
    async def test_date_dict_missing_start_raises(self) -> None:
        props = {"Due": PageDateProperty(id="d", date=None)}
        service = _make_service(props)

        with pytest.raises(
            TypeError, match=r"expects a date mapping with a string 'start' field"
        ):
            await service.set("Due", {"end": "2025-01-07"})

    @pytest.mark.asyncio
    async def test_title_wrong_type(self) -> None:
        props = {"Name": PageTitleProperty(id="t", title=[])}
        service = _make_service(props)

        with pytest.raises(TypeError, match="expects a string"):
            await service.set("Name", 42)

    @pytest.mark.asyncio
    async def test_error_message_includes_valid_options(self) -> None:
        props = {"Status": PageStatusProperty(id="s", status=None)}
        service = _make_service_with_options(props, {"Status": _STATUS_OPTION_NAMES})

        with pytest.raises(ValueError, match=r"Not started.*In progress.*Done"):
            await service.set("Status", "Invalid")

    @pytest.mark.asyncio
    async def test_relation_wrong_container_type(self) -> None:
        props = {"Module": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props)

        with pytest.raises(
            TypeError, match=r"expects a relation page id string or list\[str\]"
        ):
            await service.set("Module", 123)

    @pytest.mark.asyncio
    async def test_relation_non_string_item(self) -> None:
        props = {"Module": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props)

        with pytest.raises(TypeError, match=r"expects relation ids as strings"):
            await service.set("Module", ["11111111-1111-1111-1111-111111111111", 7])

    @pytest.mark.asyncio
    async def test_relation_empty_id_raises(self) -> None:
        props = {"Module": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props)

        with pytest.raises(ValueError, match=r"relation page id cannot be empty"):
            await service.set("Module", "   ")

    @pytest.mark.asyncio
    async def test_relation_title_resolution_without_data_source_raises(self) -> None:
        props = {"Module": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props)

        with pytest.raises(
            ValueError, match=r"cannot resolve title.*no related data source"
        ):
            await service.set("Module", "not-a-uuid")

    @pytest.mark.asyncio
    async def test_relation_title_resolves_to_page_id(self) -> None:
        props = {"Aufgaben": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props, data_source_id=DATA_SOURCE_ID)
        mock = _stub_set_property(service)

        service._http.get = AsyncMock(
            return_value={
                "properties": {
                    "Aufgaben": {
                        "type": "relation",
                        "relation": {
                            "data_source_id": "22222222-2222-2222-2222-222222222222"
                        },
                    }
                }
            }
        )
        service._http.paginate = AsyncMock(
            return_value=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "properties": {
                        "Name": {
                            "type": "title",
                            "title": [{"plain_text": "Task 1"}],
                        }
                    },
                },
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "properties": {
                        "Name": {
                            "type": "title",
                            "title": [{"plain_text": "Task 2"}],
                        }
                    },
                },
            ]
        )

        await service.set("Aufgaben", ["Task 1", "Task 2"])

        sent = mock.call_args.args[1]
        assert isinstance(sent, PageRelationProperty)
        assert [item.id for item in sent.relation] == [
            "11111111-1111-1111-1111-111111111111",
            "33333333-3333-3333-3333-333333333333",
        ]

    @pytest.mark.asyncio
    async def test_relation_title_not_found_lists_available_options(self) -> None:
        props = {"Aufgaben": PageRelationProperty(id="rel", relation=[])}
        service = _make_service(props, data_source_id=DATA_SOURCE_ID)

        service._http.get = AsyncMock(
            return_value={
                "properties": {
                    "Aufgaben": {
                        "type": "relation",
                        "relation": {
                            "data_source_id": "22222222-2222-2222-2222-222222222222"
                        },
                    }
                }
            }
        )
        service._http.paginate = AsyncMock(
            return_value=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "properties": {
                        "Name": {
                            "type": "title",
                            "title": [{"plain_text": "Task 1"}],
                        }
                    },
                },
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "properties": {
                        "Name": {
                            "type": "title",
                            "title": [{"plain_text": "Task 2"}],
                        }
                    },
                },
            ]
        )

        with pytest.raises(
            ValueError,
            match=r"Valid options: \['Task 1', 'Task 2'\]",
        ):
            await service.set("Aufgaben", ["Task 1", "Task X"])
