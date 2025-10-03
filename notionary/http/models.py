from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class HttpMethod(StrEnum):
    GET = "get"
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


@dataclass
class HttpRequest:
    method: HttpMethod
    endpoint: str
    data: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    timestamp: float = field(default_factory=time.time)
    cached_response: HttpResponse | None = None

    @property
    def cache_key(self) -> str:
        key_parts = [self.method.value, self.endpoint]

        if self.params:
            sorted_params = sorted(self.params.items())
            key_parts.extend(f"{k}={v}" for k, v in sorted_params)

        return "|".join(key_parts)

    def __repr__(self) -> str:
        return f"HttpRequest(method={self.method.value}, endpoint={self.endpoint})"


@dataclass
class HttpResponse:
    data: dict[str, Any] | None
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    from_cache: bool = False
    error: Exception | None = None

    def __repr__(self) -> str:
        return f"HttpResponse(status_code={self.status_code}, from_cache={self.from_cache})"
