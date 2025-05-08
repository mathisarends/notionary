import asyncio
from typing import Any, Awaitable, Callable

from notionary.util.logging_mixin import LoggingMixin


class PropertyValueExtractor(LoggingMixin):
    
    async def extract(
        self,
        property_name: str,
        prop_data: dict,
        relation_resolver: Callable[[str], Awaitable[Any]],
    ) -> Any:
        prop_type = prop_data.get("type")
        if not prop_type:
            return None

        handlers: dict[str, Callable[[], Awaitable[Any] | Any]] = {
            "title": lambda: "".join(
                t.get("plain_text", "") for t in prop_data.get("title", [])
            ),
            "rich_text": lambda: "".join(
                t.get("plain_text", "") for t in prop_data.get("rich_text", [])
            ),
            "number": lambda: prop_data.get("number"),
            "select": lambda: (
                prop_data.get("select", {}).get("name")
                if prop_data.get("select")
                else None
            ),
            "multi_select": lambda: [
                o.get("name") for o in prop_data.get("multi_select", [])
            ],
            "status": lambda: (
                prop_data.get("status", {}).get("name")
                if prop_data.get("status")
                else None
            ),
            "date": lambda: prop_data.get("date"),
            "checkbox": lambda: prop_data.get("checkbox"),
            "url": lambda: prop_data.get("url"),
            "email": lambda: prop_data.get("email"),
            "phone_number": lambda: prop_data.get("phone_number"),
            "relation": lambda: relation_resolver(property_name),
            "people": lambda: [p.get("id") for p in prop_data.get("people", [])],
            "files": lambda: [
                (
                    f.get("external", {}).get("url")
                    if f.get("type") == "external"
                    else f.get("name")
                )
                for f in prop_data.get("files", [])
            ],
        }

        handler = handlers.get(prop_type)
        if handler is None:
            if self.logger:
                self.logger.warning(f"Unsupported property type: {prop_type}")
            return None

        result = handler()
        return await result if asyncio.iscoroutine(result) else result
