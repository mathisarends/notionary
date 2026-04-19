"""Describe and update page properties with validation-aware APIs."""

import asyncio
from typing import Any

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def _set_if_valid(
    page: Any,
    schema: dict[str, dict[str, Any]],
    name: str,
    value: str | int | float | bool | list[str],
) -> None:
    if name not in schema:
        print(f"Skip {name!r}: property not found on this page")
        return

    info = schema[name]
    options = info.get("options")

    if isinstance(options, list):
        if isinstance(value, list):
            invalid = [v for v in value if v not in options]
            if invalid:
                print(f"Skip {name!r}: invalid option(s) {invalid}, valid: {options}")
                return
        elif isinstance(value, str) and value not in options:
            print(f"Skip {name!r}: invalid option {value!r}, valid: {options}")
            return

    await page.properties.set(name, value)
    print(f"Updated {name!r} -> {value!r}")


async def main() -> None:
    async with Notionary() as notion:
        page = await notion.pages.find("Usability-Test Ergebnisse")

        print(f"Page: {page.title}")
        print(f"URL: {page.url}\n")

        schema = page.describe_properties()
        print("Properties:")
        for name, info in schema.items():
            details = [f"type={info['type']}"]
            if info.get("current") is not None:
                details.append(f"current={info['current']!r}")
            if "options" in info:
                details.append(f"options={info['options']}")
            print(f"  - {name}: {', '.join(details)}")

        print("\nApplying updates:")
        await _set_if_valid(page, schema, "Status", "Done")
        await _set_if_valid(page, schema, "Priority", "High")
        await _set_if_valid(page, schema, "Progress", 75)


if __name__ == "__main__":
    asyncio.run(main())
