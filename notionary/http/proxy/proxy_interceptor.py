from abc import ABC, abstractmethod

from notionary.http.http_models import HttpRequest, HttpResponse


class ProxyInterceptor(ABC):
    @abstractmethod
    async def intercept_request(self, request: HttpRequest) -> HttpRequest:
        pass

    @abstractmethod
    async def intercept_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        pass
