from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from notionary.page.exceptions import PageNotFound
from notionary.page.namespace import PageNamespace
from notionary.page.properties.schemas import PageTitleProperty
from notionary.page.schemas import PageDto
from notionary.rich_text.schemas import RichText
from notionary.shared.object.schemas import WorkspaceParent
from notionary.user.schemas import PartialUserDto

PAGE_ID_1 = UUID("11111111-1111-1111-1111-111111111111")
PAGE_ID_2 = UUID("22222222-2222-2222-2222-222222222222")
USER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _user() -> PartialUserDto:
    return PartialUserDto(id=USER_ID)


def _page_dto(id: UUID, title: str) -> PageDto:
    return PageDto(
        object="page",
        id=id,
        url=f"https://notion.so/{id}",
        properties={
            "Name": PageTitleProperty(title=[RichText.from_plain_text(title)]),
        },
        parent=WorkspaceParent(type="workspace", workspace=True),
        icon=None,
        cover=None,
        in_trash=False,
        created_time="2025-01-01T00:00:00.000Z",
        created_by=_user(),
        last_edited_time="2025-06-01T00:00:00.000Z",
        last_edited_by=_user(),
    )


def _namespace_with_stream(dtos: list[PageDto]) -> PageNamespace:
    http = AsyncMock()
    ns = PageNamespace(http)

    async def fake_stream(**kwargs):
        for dto in dtos:
            yield dto

    ns._search_client.stream = fake_stream
    return ns


class TestPageNamespaceList:
    @pytest.mark.asyncio
    async def test_returns_all_pages(self) -> None:
        dtos = [_page_dto(PAGE_ID_1, "First"), _page_dto(PAGE_ID_2, "Second")]
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


class TestPageNamespaceFromTitle:
    @pytest.mark.asyncio
    async def test_exact_match_case_insensitive(self) -> None:
        dtos = [_page_dto(PAGE_ID_1, "Meeting Notes"), _page_dto(PAGE_ID_2, "Tasks")]
        ns = _namespace_with_stream(dtos)

        result = await ns.from_title("meeting notes")

        assert result.id == PAGE_ID_1

    @pytest.mark.asyncio
    async def test_raises_not_found_when_no_match(self) -> None:
        dtos = [_page_dto(PAGE_ID_1, "Notes")]
        ns = _namespace_with_stream(dtos)

        with pytest.raises(PageNotFound, match=r"No.*page.*found.*Nonexistent"):
            await ns.from_title("Nonexistent")

    @pytest.mark.asyncio
    async def test_raises_not_found_with_suggestions_for_close_match(self) -> None:
        dtos = [_page_dto(PAGE_ID_1, "Meeting Notes")]
        ns = _namespace_with_stream(dtos)

        with pytest.raises(PageNotFound) as exc_info:
            await ns.from_title("Meeting Note")

        assert "Meeting Notes" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_raises_not_found_on_empty_results(self) -> None:
        ns = _namespace_with_stream([])

        with pytest.raises(PageNotFound):
            await ns.from_title("Anything")

    @pytest.mark.asyncio
    async def test_returns_first_exact_match_when_multiple(self) -> None:
        dtos = [_page_dto(PAGE_ID_1, "Tasks"), _page_dto(PAGE_ID_2, "Tasks")]
        ns = _namespace_with_stream(dtos)

        result = await ns.from_title("Tasks")

        assert result.id == PAGE_ID_1


class TestPageNamespaceFromId:
    @pytest.mark.asyncio
    async def test_fetches_and_returns_page(self) -> None:
        dto = _page_dto(PAGE_ID_1, "Fetched Page")
        http = AsyncMock()
        http.get = AsyncMock(return_value=dto.model_dump(mode="json"))
        ns = PageNamespace(http)

        result = await ns.from_id(PAGE_ID_1)

        http.get.assert_called_once_with(f"pages/{PAGE_ID_1}")
        assert result.id == PAGE_ID_1
        assert result.title == "Fetched Page"


class TestPageNamespaceIter:
    @pytest.mark.asyncio
    async def test_yields_pages_one_by_one(self) -> None:
        dtos = [_page_dto(PAGE_ID_1, "A"), _page_dto(PAGE_ID_2, "B")]
        ns = _namespace_with_stream(dtos)

        titles = [page.title async for page in ns.iter()]

        assert titles == ["A", "B"]
