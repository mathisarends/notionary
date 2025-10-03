from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, override

from notionary.exceptions.api import NotionApiError
from notionary.http.http_client import NotionHttpClient
from notionary.http.http_models import HttpMethod, HttpRequest, HttpResponse
from notionary.http.proxy.proxy_interceptor import ProxyInterceptor
from notionary.utils.mixins.logging import LoggingMixin


@dataclass
class CacheEntry:
    response: HttpResponse
    cached_at: float


CacheStorage = dict[str, CacheEntry]


class HttpClientCachingInterceptor(ProxyInterceptor):
    def __init__(self, ttl_seconds: int = 300):
        self.cache: CacheStorage = {}
        self.ttl_seconds = ttl_seconds

    @override
    async def intercept_request(self, request: HttpRequest) -> HttpRequest:
        if self._should_skip_interception_due_to_non_idempotent_method(request):
            return request

        cache_key = request.cache_key

        if cache_key not in self.cache:
            return request

        cache_entry = self.cache[cache_key]
        if self._is_cache_expired(cache_entry):
            del self.cache[cache_key]
            return request

        cache_entry.response.from_cache = True
        request.cached_response = cache_entry.response
        return request

    def _should_skip_interception_due_to_non_idempotent_method(self, request: HttpRequest) -> bool:
        return request.method in {HttpMethod.POST, HttpMethod.PATCH, HttpMethod.DELETE}

    def _is_cache_expired(self, cache_entry: CacheEntry) -> bool:
        return (time.time() - cache_entry.cached_at) > self.ttl_seconds

    @override
    async def intercept_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        if self._is_cachable_response(request, response):
            cache_key = request.cache_key
            self.cache[cache_key] = CacheEntry(response, time.time())
        return response

    def _is_cachable_response(self, request: HttpRequest, response: HttpResponse) -> bool:
        is_okay_response_code = response.status_code >= 200 and response.status_code < 300
        return request.method == HttpMethod.GET and is_okay_response_code and response.data

    def clear_cache(self) -> None:
        self.cache.clear()


class NotionHttpClientProxy(LoggingMixin):
    def __init__(self, client: NotionHttpClient | None = None):
        self.client = client or NotionHttpClient()
        self.interceptors: list[ProxyInterceptor] = []

    def add_interceptor(self, interceptor: ProxyInterceptor) -> None:
        self.interceptors.append(interceptor)

    def remove_interceptor(self, interceptor: ProxyInterceptor) -> None:
        self.interceptors.remove(interceptor)

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self) -> None:
        await self.client.close()

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        return await self._execute_request(HttpMethod.GET, endpoint=endpoint, params=params)

    async def post(self, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any] | None:
        return await self._execute_request(HttpMethod.POST, endpoint=endpoint, data=data)

    async def patch(self, endpoint: str, data: dict[str, Any] | None = None) -> dict[str, Any] | None:
        return await self._execute_request(HttpMethod.PATCH, endpoint=endpoint, data=data)

    async def delete(self, endpoint: str) -> bool:
        result = await self._execute_request(HttpMethod.DELETE, endpoint=endpoint)
        return result is not None

    async def _execute_request(
        self,
        method: HttpMethod,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        request = HttpRequest(method, endpoint, data, params)

        for interceptor in self.interceptors:
            request = await interceptor.intercept_request(request)

        if request.cached_response:
            return await self._handle_cached_response(request)

        response = await self._execute_actual_request(method, endpoint, data, params)

        for interceptor in self.interceptors:
            response = await interceptor.intercept_response(request, response)

        return response.data

    async def _execute_actual_request(
        self,
        method: HttpMethod,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> HttpResponse:
        try:
            if method == HttpMethod.GET:
                result = await self.client.get(endpoint, params)
            elif method == HttpMethod.POST:
                result = await self.client.post(endpoint, data)
            elif method == HttpMethod.PATCH:
                result = await self.client.patch(endpoint, data)
            elif method == HttpMethod.DELETE:
                result = await self.client.delete(endpoint)
                return HttpResponse({"deleted": result}, status_code=200 if result else 404)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return HttpResponse(result, status_code=200)

        except NotionApiError as e:
            self.logger.warning(f"Notion API error: {e}")
            return HttpResponse(None, status_code=e.status_code, error=e)

        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return HttpResponse(None, status_code=500, error=e)

    async def _handle_cached_response(self, request: HttpRequest) -> dict[str, Any] | None:
        cached_response = request.cached_response

        for interceptor in self.interceptors:
            cached_response = await interceptor.intercept_response(request, cached_response)

        return cached_response.data
