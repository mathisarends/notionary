from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import httpx
import pytest
from pydantic import BaseModel

from notionary.http.client import HttpClient


def _make_client() -> HttpClient:
    return HttpClient(token="test-token")


def _mock_response(
    status_code: int, json_data: dict[str, Any] | None = None
) -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data or {}
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="error", request=MagicMock(), response=response
        )
        response.text = f"HTTP {status_code}"
    else:
        response.raise_for_status.return_value = None
    return response


def _paginated(
    results: list[Any], has_more: bool = False, next_cursor: str | None = None
) -> dict[str, Any]:
    return {"results": results, "has_more": has_more, "next_cursor": next_cursor}


@pytest.fixture
def client() -> HttpClient:
    return _make_client()


class TestHttpMethods:
    @pytest.mark.asyncio
    async def test_get_returns_json(self, client: HttpClient) -> None:
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {"id": "abc"})
            result = await client.get("/pages/abc")
        assert result == {"id": "abc"}

    @pytest.mark.asyncio
    async def test_post_sends_json_body(self, client: HttpClient) -> None:
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {"created": True})
            result = await client.post("/pages", data={"title": "hello"})
        assert result == {"created": True}
        _, call_kwargs = mock_request.call_args
        assert call_kwargs["json"] == {"title": "hello"}

    @pytest.mark.asyncio
    async def test_post_serializes_base_model(self, client: HttpClient) -> None:
        class _Item(BaseModel):
            name: str
            tag: str | None = None
            id: UUID

        model = _Item(
            name="test", tag=None, id=UUID("12345678-1234-1234-1234-123456789abc")
        )
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {"ok": True})
            await client.post("/items", data=model)
        _, call_kwargs = mock_request.call_args
        sent = call_kwargs["json"]
        assert sent == {"name": "test", "id": "12345678-1234-1234-1234-123456789abc"}
        assert "tag" not in sent

    @pytest.mark.asyncio
    async def test_patch_serializes_base_model_with_exclude_unset(
        self, client: HttpClient
    ) -> None:
        class _Update(BaseModel):
            name: str | None = None
            count: int = 0

        model = _Update(name="updated")
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {"ok": True})
            await client.patch("/items/1", data=model, exclude_unset=True)
        _, call_kwargs = mock_request.call_args
        sent = call_kwargs["json"]
        assert sent == {"name": "updated"}
        assert "count" not in sent

    @pytest.mark.asyncio
    async def test_patch_sends_json_body(self, client: HttpClient) -> None:
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {"updated": True})
            result = await client.patch("/pages/abc", data={"in_trash": True})
        assert result == {"updated": True}

    @pytest.mark.asyncio
    async def test_delete_calls_correct_method(self, client: HttpClient) -> None:
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {})
            await client.delete("/blocks/xyz")
        mock_request.assert_called_once()
        args, _ = mock_request.call_args
        assert args[0] == "DELETE"

    @pytest.mark.asyncio
    async def test_get_strips_leading_slash_from_endpoint(
        self, client: HttpClient
    ) -> None:
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {})
            await client.get("//pages/abc")
        _, call_kwargs = mock_request.call_args
        assert "//pages" not in call_kwargs.get("url", mock_request.call_args[0][1])

    @pytest.mark.asyncio
    async def test_get_with_query_params(self, client: HttpClient) -> None:
        with patch.object(
            client._client, "request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.return_value = _mock_response(200, {})
            await client.get("/pages", params={"filter": "active"})
        _, call_kwargs = mock_request.call_args
        assert call_kwargs["params"] == {"filter": "active"}


class TestPaginate:
    @pytest.mark.asyncio
    async def test_returns_all_results_from_single_page(
        self, client: HttpClient
    ) -> None:
        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = _paginated(["a", "b", "c"], has_more=False)
            results = await client.paginate("/databases/x/query")
        assert results == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_follows_pagination_cursor(self, client: HttpClient) -> None:
        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [
                _paginated(["a", "b"], has_more=True, next_cursor="cur1"),
                _paginated(["c", "d"], has_more=False),
            ]
            results = await client.paginate("/databases/x/query", page_size=2)
        assert results == ["a", "b", "c", "d"]
        assert mock_post.call_count == 2
        second_call_data = mock_post.call_args_list[1][1]["data"]
        assert second_call_data["start_cursor"] == "cur1"

    @pytest.mark.asyncio
    async def test_respects_total_results_limit(self, client: HttpClient) -> None:
        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = _paginated(
                ["a", "b", "c", "d", "e"], has_more=True
            )
            results = await client.paginate("/databases/x/query", total_results_limit=3)
        assert results == ["a", "b", "c"]
        assert mock_post.call_count == 1

    @pytest.mark.asyncio
    async def test_limit_spanning_multiple_pages(self, client: HttpClient) -> None:
        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [
                _paginated(["a", "b"], has_more=True, next_cursor="cur1"),
                _paginated(["c", "d"], has_more=True, next_cursor="cur2"),
            ]
            results = await client.paginate(
                "/databases/x/query", total_results_limit=3, page_size=2
            )
        assert results == ["a", "b", "c"]
        assert mock_post.call_count == 2

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_results(self, client: HttpClient) -> None:
        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = _paginated([], has_more=False)
            results = await client.paginate("/databases/x/query")
        assert results == []


class TestPaginateStream:
    @pytest.mark.asyncio
    async def test_yields_items_one_by_one(self, client: HttpClient) -> None:
        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = [
                _paginated([1, 2], has_more=True, next_cursor="cur1"),
                _paginated([3, 4], has_more=False),
            ]
            items = []
            async for item in client.paginate_stream("/databases/x/query", page_size=2):
                items.append(item)
        assert items == [1, 2, 3, 4]

    @pytest.mark.asyncio
    async def test_stream_respects_total_results_limit(
        self, client: HttpClient
    ) -> None:
        with patch.object(client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = _paginated([1, 2, 3, 4, 5], has_more=True)
            items = []
            async for item in client.paginate_stream(
                "/databases/x/query", total_results_limit=2
            ):
                items.append(item)
        assert items == [1, 2]
