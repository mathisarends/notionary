"""Inspect a data source property schema for agent-friendly context."""

import asyncio

from dotenv import load_dotenv

from notionary import Notionary

load_dotenv(override=True)


async def main() -> None:
    async with Notionary() as notion:
        data_source = await notion.data_sources.find("Projekte")

        print(f"Data source: {data_source.title}")
        print(f"URL: {data_source.url}\n")

        schema = await data_source.describe_properties(limit=50)
        print("Properties:")
        for name, info in schema.items():
            line = f"  - {name} [{info.type}]"

            if info.options:
                options = ", ".join(info.options)
                line += f" (options: {options})"

            if info.groups:
                groups = ", ".join(info.groups)
                line += f" (groups: {groups})"

            if info.format is not None:
                line += f" (format: {info.format})"

            if info.relation_options:
                relation_options = ", ".join(
                    f"{opt.title} [{opt.id}]" if opt.title else f"[{opt.id}]"
                    for opt in info.relation_options
                )
                line += f" (relation_options: {relation_options})"

            print(line)


if __name__ == "__main__":
    asyncio.run(main())
