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

    await page.set(name, value)
    print(f"Updated {name!r} -> {value!r}")


def _build_valid_updates(
    schema: dict[str, dict[str, Any]],
    updates: dict[str, str | int | float | bool | list[str]],
) -> dict[str, str | int | float | bool | list[str]]:
    valid_updates: dict[str, str | int | float | bool | list[str]] = {}

    for name, value in updates.items():
        if name not in schema:
            print(f"Skip {name!r}: property not found on this page")
            continue

        info = schema[name]
        options = info.get("options")

        if isinstance(options, list):
            if isinstance(value, list):
                invalid = [v for v in value if v not in options]
                if invalid:
                    print(
                        f"Skip {name!r}: invalid option(s) {invalid}, valid: {options}"
                    )
                    continue
            elif isinstance(value, str) and value not in options:
                print(f"Skip {name!r}: invalid option {value!r}, valid: {options}")
                continue

        valid_updates[name] = value

    return valid_updates


def _print_schema(schema: dict[str, dict[str, Any]]) -> None:
    print("Properties:")
    for name, info in schema.items():
        details = [f"type={info['type']}"]
        if info.get("current") is not None:
            details.append(f"current={info['current']!r}")
        if "options" in info:
            details.append(f"options={info['options']}")
        print(f"  - {name}: {', '.join(details)}")


async def main() -> None:
    async with Notionary() as notion:
        single_page = await notion.pages.find("ILIAS-CLI")
        batch_page = await notion.pages.find("Jarvis Frontend")

        print(f"Single page: {single_page.title}")
        print(f"URL: {single_page.url}\n")

        single_schema = single_page.describe_properties()
        _print_schema(single_schema)

        print("\nApplying single-property update:")
        await _set_if_valid(single_page, single_schema, "Status", "In Bearbeitung")

        print(f"\nBatch page: {batch_page.title}")
        print(f"URL: {batch_page.url}\n")

        batch_schema = batch_page.describe_properties()
        _print_schema(batch_schema)

        print("\nApplying batch update:")
        updates = {
            "Status": "In Bearbeitung",
            "Priorität": "Hoch",
            "Fortschritt": 75,
        }
        valid_updates = _build_valid_updates(batch_schema, updates)
        if valid_updates:
            await batch_page.set_properties(valid_updates)
            print(f"Updated properties: {list(valid_updates)}")
        else:
            print("No valid updates to apply.")


if __name__ == "__main__":
    asyncio.run(main())
