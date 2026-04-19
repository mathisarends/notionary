from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.properties.properties import PageProperties
from notionary.page.properties.schemas import PageTitleProperty

PAGE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def _title_property() -> PageTitleProperty:
    return PageTitleProperty(id="title", title=[])


def _make_service(properties: dict | None = None) -> tuple[PageProperties, AsyncMock]:
    http = AsyncMock()
    props = {"Name": _title_property()} if properties is None else properties
    service = PageProperties(id=PAGE_ID, properties=props, http=http)
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

        service._property_http_client.set_property.assert_called_once_with(
            "Name", "New Title"
        )

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

        service._property_http_client.set_properties.assert_called_once_with(
            {"Name": "New Title"}
        )

    @pytest.mark.asyncio
    async def test_set_properties_updates_local_properties(self) -> None:
        service, _ = _make_service()
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

        service._property_http_client.set_property.assert_called_once_with(
            "Name", "My Page Title"
        )

    @pytest.mark.asyncio
    async def test_set_title_raises_when_no_title_property(self) -> None:
        service, _ = _make_service({})

        with pytest.raises(KeyError, match="No title property"):
            await service.set_title("Title")
