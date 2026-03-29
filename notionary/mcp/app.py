import functools
import inspect
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

try:
    from fastmcp import Context, FastMCP
except ImportError as e:
    raise ImportError(
        "MCP support requires 'fastmcp'. Install with: pip install notionary[mcp]"
    ) from e

from notionary import Notionary


@asynccontextmanager
async def lifespan(_: FastMCP) -> AsyncIterator[dict]:
    async with Notionary() as client:
        yield {"notionary": client}


class NotionaryMCP(FastMCP):
    """FastMCP subclass that injects Notionary namespaces into tool functions."""

    def _namespace_tool(self, namespace: str, **tool_kwargs):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, ctx: Context, **kwargs):
                notionary: Notionary = ctx.request_context.lifespan_context["notionary"]
                return await func(
                    *args, **{namespace: getattr(notionary, namespace)}, **kwargs
                )

            sig = inspect.signature(func)
            params = [p for p in sig.parameters.values() if p.name != namespace]
            ctx_param = inspect.Parameter(
                "ctx", inspect.Parameter.KEYWORD_ONLY, annotation=Context
            )
            new_sig = sig.replace(parameters=[*params, ctx_param])
            wrapper.__signature__ = new_sig

            wrapper.__annotations__ = {
                p.name: p.annotation
                for p in new_sig.parameters.values()
                if p.annotation is not inspect.Parameter.empty
            }
            if sig.return_annotation is not inspect.Parameter.empty:
                wrapper.__annotations__["return"] = sig.return_annotation

            return self.tool(**tool_kwargs)(wrapper)

        return decorator

    def page_tool(self, **tool_kwargs):
        return self._namespace_tool("pages", **tool_kwargs)

    def database_tool(self, **tool_kwargs):
        return self._namespace_tool("databases", **tool_kwargs)

    def data_source_tool(self, **tool_kwargs):
        return self._namespace_tool("data_sources", **tool_kwargs)

    def user_tool(self, **tool_kwargs):
        return self._namespace_tool("users", **tool_kwargs)

    def workspace_tool(self, **tool_kwargs):
        return self._namespace_tool("workspace", **tool_kwargs)
