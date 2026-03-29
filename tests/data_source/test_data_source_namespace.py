from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.data_source.exceptions import DataSourceNotFound
from notionary.data_source.namespace import DataSourceNamespace
from notionary.data_source.schemas import DataSourceDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.schemas import WorkspaceParent
from notionary.user.schemas import PartialUserDto

DS_ID_1 = UUID("11111111-1111-1111-1111-111111111111")
DS_ID_2 = UUID("22222222-2222-2222-2222-222222222222")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _dto(id: UUID, title: str) -> DataSourceDto:
    return DataSourceDto(
        object="database",
        id=id,
        url=f"https://notion.so/{id}",
        title=[RichText.from_plain_text(title)],
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


def _namespace_with_stream(dtos: list[DataSourceDto]) -> DataSourceNamespace:
    http = AsyncMock()
    ns = DataSourceNamespace(http)

    async def fake_stream(**kwargs):
        for dto in dtos:
            yield dto

    ns._search_client.stream = fake_stream
    return ns


class TestList:
    @pytest.mark.asyncio
    async def test_returns_all_data_sources(self) -> None:
        dtos = [_dto(DS_ID_1, "First"), _dto(DS_ID_2, "Second")]
        ns = _namespace_with_stream(dtos)

        result = await ns.list()

        assert len(result) == 2
        assert result[0].title == "First"
        assert result[1].title == "Second"

    @pytest.mark.asyncio
    async def test_empty_stream_returns_empty_list(self) -> None:
        ns = _namespace_with_stream([])

        result = await ns.list()

        assert result == []


class TestSearch:
    @pytest.mark.asyncio
    async def test_delegates_to_list(self) -> None:
        dtos = [_dto(DS_ID_1, "Marketing")]
        ns = _namespace_with_stream(dtos)

        result = await ns.search("Marketing")

        assert len(result) == 1
        assert result[0].title == "Marketing"


class TestFromTitle:
    @pytest.mark.asyncio
    async def test_exact_match_case_insensitive(self) -> None:
        dtos = [_dto(DS_ID_1, "Sales"), _dto(DS_ID_2, "Marketing")]
        ns = _namespace_with_stream(dtos)

        result = await ns.find("sales")

        assert result.id == DS_ID_1
        assert result.title == "Sales"

    @pytest.mark.asyncio
    async def test_raises_not_found_when_no_match(self) -> None:
        dtos = [_dto(DS_ID_1, "Sales")]
        ns = _namespace_with_stream(dtos)

        with pytest.raises(
            DataSourceNotFound, match=r"No.*data source.*found.*Nonexistent"
        ):
            await ns.find("Nonexistent")

    @pytest.mark.asyncio
    async def test_raises_not_found_with_suggestions_for_close_match(self) -> None:
        dtos = [_dto(DS_ID_1, "Sales Pipeline"), _dto(DS_ID_2, "Marketing")]
        ns = _namespace_with_stream(dtos)

        with pytest.raises(DataSourceNotFound) as exc_info:
            await ns.find("Sales Pipelin")

        assert "Sales Pipeline" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_raises_not_found_on_empty_results(self) -> None:
        ns = _namespace_with_stream([])

        with pytest.raises(DataSourceNotFound):
            await ns.find("Anything")

    @pytest.mark.asyncio
    async def test_returns_first_exact_match_when_multiple(self) -> None:
        dtos = [_dto(DS_ID_1, "Tasks"), _dto(DS_ID_2, "Tasks")]
        ns = _namespace_with_stream(dtos)

        result = await ns.find("Tasks")

        assert result.id == DS_ID_1


class TestFromId:
    @pytest.mark.asyncio
    async def test_fetches_and_returns_data_source(self) -> None:
        dto = _dto(DS_ID_1, "Fetched DB")
        http = AsyncMock()
        http.get = AsyncMock(return_value=dto.model_dump(mode="json"))
        ns = DataSourceNamespace(http)

        result = await ns.from_id(DS_ID_1)

        http.get.assert_called_once_with(f"databases/{DS_ID_1}")
        assert result.id == DS_ID_1
        assert result.title == "Fetched DB"


class TestIter:
    @pytest.mark.asyncio
    async def test_yields_data_sources_one_by_one(self) -> None:
        dtos = [_dto(DS_ID_1, "A"), _dto(DS_ID_2, "B")]
        ns = _namespace_with_stream(dtos)

        titles = [ds.title async for ds in ns.iter()]

        assert titles == ["A", "B"]
