from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.properties.properties import PageProperties
from notionary.page.properties.schemas import (
    PageSelectProperty,
    PageStatusProperty,
    PageTitleProperty,
    SelectOption,
    StatusOption,
)
from notionary.rich_text.schemas import RichText

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
DATA_SOURCE_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


def _title_property() -> PageTitleProperty:
    return PageTitleProperty(id="title", title=[])


def _status_property(options: list[StatusOption] | None = None) -> PageStatusProperty:
    return PageStatusProperty(id="status", status=None, options=options or [])


def _select_property(options: list[SelectOption] | None = None) -> PageSelectProperty:
    return PageSelectProperty(id="select", select=None, options=options or [])


def _make_service(
    properties: dict | None = None,
    data_source_id: UUID | None = None,
) -> tuple[PageProperties, AsyncMock]:
    http = AsyncMock()
    props = {"Name": _title_property()} if properties is None else properties
    service = PageProperties(
        id=PAGE_ID,
        properties=props,
        http=http,
        data_source_id=data_source_id,
    )
    return service, http


class TestPagePropertiesSetProperty:
    @pytest.mark.asyncio
    async def test_set_property_delegates_to_http_client(self) -> None:
        service, _ = _make_service()
        updated_props = {"Name": _title_property()}
        service._property_http_client.set_property = AsyncMock(
            return_value=type("Dto", (), {"properties": updated_props})()
        )

        await service.set_property("Name", "New Title")

        call_args = service._property_http_client.set_property.call_args
        assert call_args is not None
        assert call_args.args[0] == "Name"
        sent_property = call_args.args[1]
        assert isinstance(sent_property, PageTitleProperty)
        assert sent_property.title == [
            RichText(type="text", text={"content": "New Title"})
        ]

    @pytest.mark.asyncio
    async def test_set_property_updates_local_properties(self) -> None:
        service, _ = _make_service()
        new_props = {"Name": _title_property(), "Status": _title_property()}
        service._property_http_client.set_property = AsyncMock(
            return_value=type("Dto", (), {"properties": new_props})()
        )

        await service.set_property("Name", "Updated")

        assert service.properties == new_props

    @pytest.mark.asyncio
    async def test_set_properties_delegates_to_http_client(self) -> None:
        service, _ = _make_service()
        updated_props = {"Name": _title_property()}
        service._property_http_client.set_properties = AsyncMock(
            return_value=type("Dto", (), {"properties": updated_props})()
        )

        await service.set_properties({"Name": "New Title"})

        call_args = service._property_http_client.set_properties.call_args
        assert call_args is not None
        sent_properties = call_args.args[0]
        sent_name = sent_properties["Name"]
        assert isinstance(sent_name, PageTitleProperty)
        assert sent_name.title == [RichText(type="text", text={"content": "New Title"})]

    @pytest.mark.asyncio
    async def test_set_properties_updates_local_properties(self) -> None:
        service, _ = _make_service(
            {
                "Name": _title_property(),
                "Status": _status_property(
                    [
                        StatusOption(id="1", name="Not started"),
                        StatusOption(id="2", name="Done"),
                    ]
                ),
            }
        )
        new_props = {"Name": _title_property(), "Status": _title_property()}
        service._property_http_client.set_properties = AsyncMock(
            return_value=type("Dto", (), {"properties": new_props})()
        )

        await service.set_properties({"Name": "Updated", "Status": "Done"})

        assert service.properties == new_props


class TestPagePropertiesSetTitle:
    @pytest.mark.asyncio
    async def test_set_title_finds_title_property_and_sets_it(self) -> None:
        service, _ = _make_service({"Name": _title_property()})
        service._property_http_client.set_property = AsyncMock(
            return_value=type("Dto", (), {"properties": {"Name": _title_property()}})()
        )

        await service.set_title("My Page Title")

        call_args = service._property_http_client.set_property.call_args
        assert call_args is not None
        assert call_args.args[0] == "Name"
        sent_property = call_args.args[1]
        assert isinstance(sent_property, PageTitleProperty)
        assert sent_property.title == [
            RichText(type="text", text={"content": "My Page Title"})
        ]

    @pytest.mark.asyncio
    async def test_set_title_raises_when_no_title_property(self) -> None:
        service, _ = _make_service({})

        with pytest.raises(KeyError, match="No title property"):
            await service.set_title("Title")


class TestPagePropertiesSetWithDataSourceOptions:
    @pytest.mark.asyncio
    async def test_set_property_uses_data_source_options_for_status(self) -> None:
        service, http = _make_service(
            properties={"Status": _status_property()},
            data_source_id=DATA_SOURCE_ID,
        )
        service._property_http_client.set_property = AsyncMock(
            return_value=type("Dto", (), {"properties": service.properties})()
        )
        http.get = AsyncMock(
            return_value={
                "properties": {
                    "Status": {
                        "type": "status",
                        "status": {
                            "options": [
                                {"name": "Nicht begonnen"},
                                {"name": "In Bearbeitung"},
                                {"name": "Erledigt"},
                            ]
                        },
                    }
                }
            }
        )

        await service.set_property("Status", "In Bearbeitung")

        call_args = service._property_http_client.set_property.call_args
        assert call_args is not None
        assert call_args.args[0] == "Status"
        sent_property = call_args.args[1]
        assert isinstance(sent_property, PageStatusProperty)
        assert sent_property.status is not None
        assert sent_property.status.name == "In Bearbeitung"

    @pytest.mark.asyncio
    async def test_set_property_raises_with_resolved_options(self) -> None:
        service, _ = _make_service(properties={"Status": _status_property()})
        service._data_source_option_names = {
            "Status": ["Nicht begonnen", "In Bearbeitung", "Erledigt"]
        }

        with pytest.raises(
            ValueError,
            match=r"Valid options: \['Nicht begonnen', 'In Bearbeitung', 'Erledigt'\]",
        ):
            await service.set_property("Status", "Fertig")

    @pytest.mark.asyncio
    async def test_set_properties_validates_select_and_status_from_data_source(
        self,
    ) -> None:
        service, http = _make_service(
            properties={
                "Status": _status_property(),
                "Priorität": _select_property(),
            },
            data_source_id=DATA_SOURCE_ID,
        )
        service._property_http_client.set_properties = AsyncMock(
            return_value=type("Dto", (), {"properties": service.properties})()
        )
        http.get = AsyncMock(
            return_value={
                "properties": {
                    "Status": {
                        "type": "status",
                        "status": {
                            "options": [
                                {"name": "Nicht begonnen"},
                                {"name": "In Bearbeitung"},
                                {"name": "Erledigt"},
                            ]
                        },
                    },
                    "Priorität": {
                        "type": "select",
                        "select": {
                            "options": [
                                {"name": "Hoch"},
                                {"name": "Mittel"},
                                {"name": "Niedrig"},
                            ]
                        },
                    },
                }
            }
        )

        await service.set_properties(
            {
                "Status": "In Bearbeitung",
                "Priorität": "Hoch",
            }
        )

        call_args = service._property_http_client.set_properties.call_args
        assert call_args is not None
        sent_properties = call_args.args[0]

        sent_status = sent_properties["Status"]
        assert isinstance(sent_status, PageStatusProperty)
        assert sent_status.status is not None
        assert sent_status.status.name == "In Bearbeitung"

        sent_priority = sent_properties["Priorität"]
        assert isinstance(sent_priority, PageSelectProperty)
        assert sent_priority.select is not None
        assert sent_priority.select.name == "Hoch"
